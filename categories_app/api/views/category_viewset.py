from typing import Iterable
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from categories_app.models import Category
from categories_app.api.serializers import CategorySerializer
from categories_app.lib.category_tree import CategoryTree


class CategoryListMixin:
    """
    Filterable by query params:
        - name (case insensitive, partial match)
        - ancestor_id (only categories that are descendants of the category with this id)
        - max_depth (limits how deep the descendants can be)
            - when used with ancestor_id, it is considered depth=0
            - when used without ancestor_id, top-level categories are considered depth=0

    Orderable by name, parent, created_at, updated_at, e.g. ?order_by=name.
    Reverse ordering e.g. ?order_by=-name.

    Pagination (with default settings) comes our of the box.
    """

    _orderable_fields: set[str] = {"name", "parent", "created_at", "updated_at"}

    def list(self, request):
        self._parse_query_params()
        queryset = self._filter_queryset(self.queryset)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def _parse_query_params(self):
        self.qparam_name: str | None = None
        self.qparam_ancestor_id: int | None = None
        self.qparam_max_depth: int | None = None
        self.qparam_order_by: str | None = None

        self.qparam_name = self.request.query_params.get("name")

        if ancestor_id_str := self.request.query_params.get("ancestor_id"):
            err_msg = "query param ancestor_id must be a positive integer"
            try:
                self.qparam_ancestor_id = int(ancestor_id_str)
            except ValueError:
                raise ValidationError(err_msg)

            if self.qparam_ancestor_id < 1:
                raise ValidationError(err_msg)

        if max_depth_str := self.request.query_params.get("max_depth"):
            err_msg = "query param max_depth must be a nonnegative integers"
            try:
                self.qparam_max_depth = int(max_depth_str)
            except ValueError:
                raise ValidationError(err_msg)

            if self.qparam_max_depth < 0:
                raise ValidationError(err_msg)

        self.qparam_order_by = self.request.query_params.get("order_by")
        if self.qparam_order_by:
            field_name = self.qparam_order_by.lstrip("-")
            if field_name not in self._orderable_fields:
                raise ValidationError(f"Invalid order_by field: {field_name}")

    def _filter_queryset(self, queryset: QuerySet[Category]) -> Iterable[Category]:
        queryset = Category.objects.all()

        if self.qparam_order_by:
            queryset = queryset.order_by(self.qparam_order_by)

        if self.qparam_name:
            queryset = queryset.filter(name__icontains=self.qparam_name)

        category_tree = CategoryTree(list(Category.objects.all()))
        queryset = category_tree.filter(
            queryset=queryset,
            ancestor_id=self.qparam_ancestor_id,
            max_depth=self.qparam_max_depth,
        )

        return queryset


class CategoryRetrieveMixin:
    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category)
        return Response(serializer.data)


class CategoryCreateMixin:
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                self.serializer_class(category).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDestroyMixin:
    """
    Delete a category and move its children to the deleted category's parent.
    """

    @transaction.atomic
    # TODO: Consider using transactions per HTTP request for simplicity at the cost of a bit of performance.
    def destroy(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)

        Category.objects.filter(parent=category).update(parent=category.parent)
        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryUpdateMixin:
    def partial_update(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)

        serializer = self.serializer_class(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(
    CategoryListMixin,
    CategoryRetrieveMixin,
    CategoryCreateMixin,
    CategoryDestroyMixin,
    CategoryUpdateMixin,
    viewsets.ViewSet,
):
    serializer_class = CategorySerializer
    queryset: QuerySet[Category] = Category.objects.all()
