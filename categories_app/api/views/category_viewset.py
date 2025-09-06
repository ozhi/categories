from typing import Iterable
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from categories_app.models import Category
from categories_app.api.serializers import CategorySerializer


class CategoryListMixin:
    """
    Pagination (with default settings) comes our of the box.
    Filterable by query params:
        - name (case insensitive, partial match)
        - ancestor_id (only categories that are descendants of the category with this id)
        - max_depth (when used with ancestor_id, limits how deep the descendants can be)
    """

    def list(self, request):
        self._parse_query_params()
        queryset = self._filter_queryset(self.queryset)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def _parse_query_params(self):
        self.qparam_name: str | None = None
        self.qparam_ancestor_id: int | None = None
        self.qparam_max_depth: int | None = None

        self.qparam_name = self.request.query_params.get("name")

        if ancestor_id_str := self.request.query_params.get("ancestor_id"):
            try:
                self.qparam_ancestor_id = int(ancestor_id_str)
            except ValueError:
                raise ValidationError(
                    "query param ancestor_id must be a positive integer"
                )

            if self.qparam_ancestor_id < 1:
                raise ValidationError(
                    "query param ancestor_id must be a positive integer"
                )

        if max_depth_str := self.request.query_params.get("max_depth"):
            try:
                self.qparam_max_depth = int(max_depth_str)
            except ValueError:
                raise ValidationError(
                    "query param max_depth must be a nonnegative integers"
                )

            if self.qparam_max_depth < 0:
                raise ValidationError(
                    "query param max_depth must be a nonnegative integers"
                )

    def _filter_queryset(self, queryset: QuerySet[Category]) -> Iterable[Category]:
        queryset = Category.objects.all()

        if self.qparam_name:
            queryset = queryset.filter(name__icontains=self.qparam_name)

        if self.qparam_ancestor_id:
            # Fetch all categories from db and
            # perform ancestor and depth filtering in Python rather than SQL for simplicity.

            # Make sure to precalculate ancestors and depths for all categories, not just filtered queryset.
            # This keeps different filters independent and applicable simultaneously.
            ancestors: dict[int, int] = {}
            depths: dict[int, int] = {}
            all_categories = list(Category.objects.all())
            category_map: dict[int, Category] = {
                category.id: category for category in all_categories
            }

            for category in all_categories:
                self._determine_ancestor_and_depth(
                    category.id, category_map, ancestors, depths
                )

            queryset = [
                category
                for category in queryset
                if self._category_matches_ancestor_and_depth(
                    category.id,
                    self.qparam_ancestor_id,
                    self.qparam_max_depth,
                    category_map,
                    ancestors,
                    depths,
                )
            ]

        return queryset

    @classmethod
    def _determine_ancestor_and_depth(
        cls,
        category_id: int,
        category_map: dict[int, Category],
        ancestors: dict[int, int],
        depths: dict[int, int],
    ) -> None:
        if category_id in ancestors and category_id in depths:
            return

        parent_id = category_map[category_id].parent_id
        if parent_id is None:
            ancestors[category_id] = None
            depths[category_id] = 0
            return

        cls._determine_ancestor_and_depth(parent_id, category_map, ancestors, depths)

        ancestors[category_id] = ancestors[parent_id]
        depths[category_id] = depths[parent_id] + 1

    @classmethod
    def _category_matches_ancestor_and_depth(
        cls,
        category_id: int,
        target_ancestor_id: int,
        max_depth: int,
        category_map: dict[int, Category],
        ancestors: dict[int, int],
        depths: dict[int, int],
    ) -> bool:
        if max_depth is not None and max_depth < 0:
            return False

        if category_id is None:
            return False

        if category_id == target_ancestor_id:
            return True

        return cls._category_matches_ancestor_and_depth(
            category_map[category_id].parent_id,
            target_ancestor_id,
            max_depth - 1 if max_depth is not None else None,
            category_map,
            ancestors,
            depths,
        )


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
    def destroy(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)

        Category.objects.filter(parent=category).update(parent=category.parent)
        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryUpdateMixin:
    def update(self, request, pk=None, partial=False):
        category = get_object_or_404(self.queryset, pk=pk)

        serializer = self.serializer_class(category, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)


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
