import pytest
from rest_framework.test import APIClient
from categories_app.models import Category


@pytest.mark.django_db
class TestCategoryViewSetList:
    def setup_method(self):
        self.client = APIClient()

    def test_list(self, categories):
        response = self.client.get("/api/categories/")
        assert response.status_code == 200

        returned_category_names = [cat["name"] for cat in response.data]
        assert len(returned_category_names) == len(categories)
        assert "Laptops" in returned_category_names
        assert "Potatoes" in returned_category_names

    def test_filter_by_name_partial_match(self, categories):
        response = self.client.get("/api/categories/?name=p")
        assert response.status_code == 200

        returned_category_names = [cat["name"] for cat in response.data]
        assert len(returned_category_names) == 10
        assert "Laptops" in returned_category_names
        assert "Potatoes" in returned_category_names
        assert "Food" not in returned_category_names

    def test_filter_by_ancestor_invalid_string(self, categories):
        response = self.client.get("/api/categories/?ancestor_id=seven")
        assert response.status_code == 400
        assert "ancestor_id" in str(response.data).lower()

    def test_filter_by_ancestor_invalid_invalid(self, categories):
        response = self.client.get("/api/categories/?ancestor_id=0")
        assert response.status_code == 400
        assert "ancestor_id" in str(response.data).lower()

    def test_filter_by_max_depth_invalid_negative(self, categories):
        response = self.client.get("/api/categories/?max_depth=-1")
        assert response.status_code == 400
        assert "max_depth" in str(response.data).lower()

    def test_filter_by_max_depth_invalid_string(self, categories):
        response = self.client.get("/api/categories/?max_depth=seven")
        assert response.status_code == 400
        assert "max_depth" in str(response.data).lower()

    def test_filter_by_ancestor(self, categories):
        response = self.client.get(
            f"/api/categories/?ancestor_id={categories['Computers'].id}",
        )
        assert response.status_code == 200

        returned_category_names = [cat["name"] for cat in response.data]
        assert len(returned_category_names) == 3
        assert "Computers" in returned_category_names
        assert "Laptops" in returned_category_names
        assert "Desktops" in returned_category_names

    def test_filter_by_max_depth(self, categories):
        response = self.client.get("/api/categories/?max_depth=0")
        assert response.status_code == 200

        returned_category_names = [cat["name"] for cat in response.data]
        assert len(returned_category_names) == 3
        assert "Tech" in returned_category_names
        assert "Food" in returned_category_names
        assert "Books" in returned_category_names

    def test_filter_by_ancestor_and_max_depth(self, categories):
        response = self.client.get(
            f"/api/categories/?ancestor_id={categories['Tech'].id}&max_depth=2",
        )
        assert response.status_code == 200

        returned_category_names = [cat["name"] for cat in response.data]
        expected_category_names = [
            "Tech",
            "Computers",
            "Laptops",
            "Desktops",
            "Audio",
            "Headphones",
        ]
        assert len(returned_category_names) == len(expected_category_names)
        for name in expected_category_names:
            assert name in returned_category_names


@pytest.mark.django_db
class TestCategoryViewSet:
    def setup_method(self):
        self.client = APIClient()

    def test_retrieve(self, categories):
        response = self.client.get(f"/api/categories/{categories['Potatoes'].id}/")
        assert response.status_code == 200
        assert response.data["name"] == "Potatoes"
        assert response.data["parent"] == categories["Vegetables"].id

    def test_create(self, categories):
        parent_id = categories["Books"].id
        response = self.client.post(
            "/api/categories/",
            {
                "name": "Novels",
                "parent": parent_id,
            },
        )
        assert response.status_code == 201
        assert Category.objects.filter(name="Novels").exists()
        category = Category.objects.get(name="Novels")
        assert category.parent_id == parent_id

    def test_partial_update(self, categories):
        potatoes = Category.objects.get(id=categories["Potatoes"].id)
        assert potatoes.parent == Category.objects.get(id=categories["Vegetables"].id)

        response = self.client.patch(
            f"/api/categories/{categories['Potatoes'].id}/",
            {"name": "Taters"},
        )
        assert response.status_code == 200

        potatoes.refresh_from_db()
        assert potatoes.name == "Taters"
        assert potatoes.description is None
        # Partial update keeps existing fields.
        assert potatoes.parent_id == categories["Vegetables"].id

    def test_destroy_category_reassigns_children(self, categories):
        computers = categories["Computers"]
        laptops = Category.objects.get(id=categories["Laptops"].id)
        desktops = Category.objects.get(id=categories["Desktops"].id)
        assert laptops.parent_id == computers.id
        assert desktops.parent_id == computers.id

        response = self.client.delete(f"/api/categories/{computers.id}/")
        assert response.status_code == 204

        laptops.refresh_from_db()
        desktops.refresh_from_db()
        assert laptops.parent_id == computers.parent_id
        assert desktops.parent_id == computers.parent_id
