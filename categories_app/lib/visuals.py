import anytree
import anytree.exporter
from django.db.models import Prefetch

from categories_app.lib.similarity_graph import SimilarityGraph
from categories_app.models import Category
from .colors import X11_COLOR_NAMES


class CategoryVisuals:
    def __init__(self) -> None:
        all_categories = Category.objects.prefetch_related(
            Prefetch("similar_to", queryset=Category.objects.only("id"))
        ).all()

        self.categories: dict[int, Category] = {
            category.id: category for category in all_categories
        }

        similarity_graph = SimilarityGraph()
        self.anytree_root = self._construct_anytree(similarity_graph)

    def _construct_anytree(self, similarity_graph: SimilarityGraph) -> anytree.Node:
        nodes: dict[int, anytree.Node] = {}
        for category in self.categories.values():
            nodes[category.id] = anytree.Node(category.name, category_id=category.id)

        # anytree operates on a single tree.
        # Create a dummy root as the parent of our set of category trees.
        dummy_root = anytree.Node("dummy_root", category_id=-1, color="black")
        for category in self.categories.values():
            if category.parent_id is None:
                nodes[category.id].parent = dummy_root
            else:
                nodes[category.id].parent = nodes[category.parent_id]

        islands = similarity_graph.compute_rabbit_islands()
        for i, island in enumerate(islands):
            for category_id in island:
                nodes[category_id].color = X11_COLOR_NAMES[i % len(X11_COLOR_NAMES)]

        return dummy_root

    def tree_as_string(self) -> str:
        s = ""
        for pre, fill, node in anytree.RenderTree(self.anytree_root):
            s += pre + node.name + "\n"
        return s

    def save_tree_as_image(self, filename: str) -> None:
        anytree.exporter.UniqueDotExporter(
            self.anytree_root,
            nodeattrfunc=lambda node: f"style=filled,fillcolor={node.color}",
            nodenamefunc=lambda node: node.name,
        ).to_picture(filename)
