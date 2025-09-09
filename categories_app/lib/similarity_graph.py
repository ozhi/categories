from collections import deque

from django.db.models import Prefetch

from categories_app.models import Category


class SimilarityGraph:
    """
    Represents the set of Categories when regarded as a graph with similarity relationships.

    Complexity:
    V (Vertices, categories) = 2*10^3
    E (Edges, similarities) = 2*10^5
    Unweighted graph, so we don't need Dijkstra or Floyd-Warshall algorithm.

    BFS = O(E+V) = 2*10^5
    longest_rabbit_hole (repeated BFS) = O(V*(E+V)) = 4 *10^8

    DFS = O(V+E) = 2*10^5
    rabbit_islands (repeated DFS, but each vertex visited once) = 2*10^5
    """

    def __init__(self):
        # Prefetch similars for each category to avoid N+1 problem.
        # This results in just 2 db queries.
        all_categories = Category.objects.prefetch_related(
            Prefetch("similar_to", queryset=Category.objects.only("id"))
        ).all()

        self.categories: dict[int, Category] = {
            category.id: category for category in all_categories
        }

    def compute_longest_rabbit_hole(self) -> list[int]:
        max_dist: int = 0
        longest_rabbit_hole: list[int] = []
        for id in self.categories.keys():
            distances, parents = self._bfs(id)

            for category_id, dist in distances.items():
                if dist > max_dist:
                    max_dist = dist
                    longest_rabbit_hole = self._get_path(category_id, parents)

        return longest_rabbit_hole

    def _get_path(self, end_id: int, parents: dict[int, int]) -> list[int]:
        id = end_id
        path: list[int] = []
        while id:
            path.append(id)
            id = parents[id]
        return list(reversed(path))

    def _bfs(self, start_id: int) -> tuple[dict[int, int], dict[int, int]]:
        queue: deque[int] = deque([start_id])
        dist_from_start: dict[int, int] = {start_id: 0}
        parents: dict[int, int] = {start_id: None}

        while queue:
            id = queue.popleft()

            for neighbor in self.categories[id].similar_to.all():
                if neighbor.id not in dist_from_start:
                    dist_from_start[neighbor.id] = dist_from_start[id] + 1
                    parents[neighbor.id] = id
                    queue.append(neighbor.id)

        return dist_from_start, parents

    def compute_rabbit_islands(self) -> list[set[int]]:
        visited: set[int] = set()
        islands: list[set[int]] = []
        for id in self.categories.keys():
            if id in visited:
                continue

            island = self._dfs(id, visited)
            islands.append(island)
        return islands

    def _dfs(self, start_id: int, visited: set[int]) -> set[int]:
        stack = [start_id]
        island = set()

        while stack:
            id = stack.pop()
            if id in visited:
                continue

            visited.add(id)
            island.add(id)
            for neighbor in self.categories[id].similar_to.all():
                if neighbor.id not in visited:
                    stack.append(neighbor.id)

        return island
