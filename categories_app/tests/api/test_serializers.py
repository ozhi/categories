import pytest
from rest_framework.exceptions import ValidationError
from categories_app.models import Category
from categories_app.api.serializers import (
    CategorySerializer,
    CategorySimilarityAddSerializer,
)


@pytest.mark.django_db
class TestCategorySerializer:
    def test_serialization(self, categories):
        data = CategorySerializer(categories["Computers"]).data
        assert data["name"] == "Computers"
        assert data["description"] == "Thinking machines"
        assert data["parent"] == categories["Tech"].id

    def test_deserialization_valid(self, categories):
        data = {
            "name": "Tomatoes",
            "description": "Red",
            "parent": categories["Vegetables"].id,
        }
        serializer = CategorySerializer(data=data)

        assert serializer.is_valid(), serializer.errors
        category = serializer.save()
        assert category.name == "Tomatoes"
        assert category.description == "Red"
        assert category.parent == categories["Vegetables"]

    def test_validate_self_parent_forbidden(self):
        cat = Category.objects.create(name="Root")
        serializer = CategorySerializer(cat, data={"parent": cat.id}, partial=True)
        assert not serializer.is_valid()
        assert "A category cannot be its own parent." in str(serializer.errors)

    def test_validate_cycle_detection(self):
        root = Category.objects.create(name="Root")
        child = Category.objects.create(name="Child", parent=root)
        serializer = CategorySerializer(root, data={"parent": child.id}, partial=True)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestCategorySimilarityAddSerializer:
    def test_valid_data(self):
        serializer = CategorySimilarityAddSerializer(data={"id": 5})
        assert serializer.is_valid()
        assert serializer.validated_data["id"] == 5

    def test_invalid_data(self):
        serializer = CategorySimilarityAddSerializer(data={})
        assert not serializer.is_valid()
