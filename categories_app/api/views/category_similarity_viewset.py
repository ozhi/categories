from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from categories_app.models import Category
from categories_app.api.serializers import (
    CategorySerializer,
    CategorySimilarityAddSerializer,
)


class CategorySimilarityViewSet(viewsets.ViewSet):
    """
    Handles /categories/{category_pk}/similarities/
    """

    def get_category(self):
        return get_object_or_404(Category, pk=self.kwargs["category_pk"])

    def list(self, request, category_pk=None):
        category = self.get_category()
        similarities = category.similar_to.all()
        serializer = CategorySerializer(similarities, many=True)
        return Response(serializer.data)

    def create(self, request, category_pk=None):
        category = self.get_category()
        serializer = CategorySimilarityAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        similar_category = get_object_or_404(
            Category, pk=serializer.validated_data["id"]
        )
        if similar_category == category:
            return Response(
                {"detail": "A category cannot be similar to itself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category.similar_to.add(similar_category)
        return Response(
            CategorySerializer(similar_category).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request, pk=None, category_pk=None):
        category = self.get_category()
        similar_category = get_object_or_404(Category, pk=pk)
        category.similar_to.remove(similar_category)
        return Response(status=status.HTTP_204_NO_CONTENT)
