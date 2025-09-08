import pytest
from categories_app.lib.db_seed import create_example_categories


@pytest.fixture
def categories(db):
    return create_example_categories()
