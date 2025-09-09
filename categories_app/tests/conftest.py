import pytest

from django.core.cache import cache

from categories_app.lib.db_seed import create_example_categories


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def categories(db):
    return create_example_categories()
