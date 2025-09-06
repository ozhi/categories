from typing import Iterable

from categories_app.models import Category


class CategoryTree:
    """
    Represents the set of Categories when regarded as a tree of parent/child relationships.
    Filtering is done here as python is better suited for such recursive relationships than SQL.
    Should be initialized with all Categories for complete depth evaluation.
    """

    def __init__(self, all_categories: Iterable[Category]):
        self.ancestors: dict[int, int] = {}
        self.depths: dict[int, int] = {}
        self.categories: dict[int, Category] = {
            category.id: category for category in all_categories
        }

        for category in all_categories:
            self._memoize_depth(category.id)

    def _memoize_depth(self, category_id: int) -> None:
        if category_id in self.depths:
            return

        parent_id = self.categories[category_id].parent_id
        if parent_id is None:
            self.depths[category_id] = 0
            return

        self._memoize_depth(parent_id)

        self.depths[category_id] = self.depths[parent_id] + 1

    def filter(
        self,
        queryset: Iterable[Category],
        ancestor_id: int | None,
        max_depth: int | None,
    ) -> Iterable[Category]:
        if ancestor_id is None:
            if max_depth is None:
                return queryset

            return [c for c in queryset if self.depths[c.id] <= max_depth]

        return [
            c
            for c in queryset
            if self._category_has_ancestor(c.id, ancestor_id, max_depth)
        ]

    def _category_has_ancestor(
        self,
        category_id: int | None,
        ancestor_id: int,
        max_depth: int | None,
    ) -> bool:
        if category_id is None:
            return False

        if max_depth is not None and max_depth < 0:
            return False

        if category_id == ancestor_id:
            return True

        return self._has_ancestor(
            self.categories[category_id].parent_id,
            ancestor_id,
            max_depth - 1 if max_depth is not None else None,
        )
