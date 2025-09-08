import pytest
from rest_framework.test import APIClient
from categories_app.models import Category


@pytest.mark.django_db
class TestCategorySimilarityViewSet:
    def setup_method(self):
        self.client = APIClient()

    def test_list_similarities(self, categories):
        response = self.client.get(
            f"/api/categories/{categories['Laptops'].id}/similarities/"
        )
        assert response.status_code == 200

        returned_category_names = [category["name"] for category in response.data]
        assert len(returned_category_names) == 2
        assert "Computers" in returned_category_names
        assert "Desktops" in returned_category_names

    def test_create_similarity_symmetric(self, categories):
        response = self.client.post(
            f"/api/categories/{categories['Tech'].id}/similarities/",
            {"id": categories["Potatoes"].id},
        )
        assert response.status_code == 201
        assert (
            categories["Potatoes"]
            in Category.objects.get(id=categories["Tech"].id).similar_to.all()
        )
        assert (
            categories["Tech"]
            in Category.objects.get(id=categories["Potatoes"].id).similar_to.all()
        )

    def test_create_similarity_self_forbidden(self, categories):
        id = categories["Tech"].id
        response = self.client.post(
            f"/api/categories/{id}/similarities/",
            {"id": id},
        )
        assert response.status_code == 400
        assert "cannot be similar to itself" in str(response.data).lower()

    def test_destroy_similarity(self, categories):
        assert categories["Laptops"] in categories["Desktops"].similar_to.all()
        assert categories["Desktops"] in categories["Laptops"].similar_to.all()

        response = self.client.delete(
            f"/api/categories/{categories['Laptops'].id}/similarities/{categories['Desktops'].id}/"
        )
        assert response.status_code == 204

        categories["Desktops"].refresh_from_db()
        categories["Laptops"].refresh_from_db()
        assert categories["Laptops"] not in categories["Desktops"].similar_to.all()
        assert categories["Desktops"] not in categories["Laptops"].similar_to.all()
