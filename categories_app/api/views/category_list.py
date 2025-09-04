from typing import Iterable
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from categories_app.models import Category
from categories_app.api.serializers import CategorySerializer

class CategoryListView(generics.ListAPIView):
    """
    Pagination (with default settings) comes our of the box.
    Filterable by query params:
        - name (case insensitive, partial match)
        - ancestor_id (only categories that are descendants of the category with this id)
        - max_depth (when used with ancestor_id, limits how deep the descendants can be)
    """
    
    serializer_class = CategorySerializer

    def get_queryset(self) -> Iterable[Category]:
        queryset = Category.objects.all()

        self._parse_query_params() # TODO move to list method override?

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
                category for category in queryset
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
                    "query param max_depth must be a positive integers"
                )

            if self.qparam_max_depth < 1:
                raise ValidationError(
                    "query param max_depth must be a positive integers"
                )

    @staticmethod
    def _determine_ancestor_and_depth(
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

        CategoryListView._determine_ancestor_and_depth(parent_id, category_map, ancestors, depths)

        ancestors[category_id] = ancestors[parent_id]
        depths[category_id] = depths[parent_id] + 1

    @staticmethod
    def _category_matches_ancestor_and_depth(
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

        return CategoryListView._category_matches_ancestor_and_depth(
            category_map[category_id].parent_id,
            target_ancestor_id,
            max_depth - 1 if max_depth is not None else None,
            category_map,
            ancestors,
            depths,
        )
