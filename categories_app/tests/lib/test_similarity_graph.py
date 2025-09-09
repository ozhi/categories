import pytest
from categories_app.models import Category
from categories_app.lib.similarity_graph import SimilarityGraph


@pytest.mark.django_db
class TestSimilarityGraph:
    def test_compute_longest_rabbit_hole(self, categories):
        graph = SimilarityGraph()

        path = graph.compute_longest_rabbit_hole()
        assert len(path) == 3
        for name in ["Computers", "Laptops", "Books"]:
            assert categories[name].id in path

    def test_compute_rabbit_islands(self, categories):
        graph = SimilarityGraph()

        islands = graph.compute_rabbit_islands()
        assert len(islands) == 11

        islands_by_name = [
            {_categories_by_id(categories, id) for id in island} for island in islands
        ]

        # Expected islands:
        # - {Computers, Laptops, Desktops, Books}
        # - {Potatoes, Sweet potatoes}
        # - Everything else is isolated single-category islands
        assert {"Computers", "Laptops", "Desktops", "Books"} in islands_by_name
        assert {"Potatoes", "Sweet potatoes"} in islands_by_name

        total_nodes = sum(len(island) for island in islands)
        assert total_nodes == len(categories)


def _categories_by_id(categories: dict[str, Category], category_id) -> Category:
    for name, category in categories.items():
        if category.id == category_id:
            return name
    raise ValueError(f"Category id {category_id} not found")
