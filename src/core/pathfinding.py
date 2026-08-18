from .interfaces import PathFinder
from .models.graph import Graph

import heapq
from .models.node import Node

from .models.route import Route


class Dijkstra(PathFinder):
    def __init__(
        self,
        graph: Graph
    ):
        self.graph = graph

    def find_path_to(self, end_node: Node,) -> tuple[list[Node], float] | None:
        start_node = self.graph.start_node
        distances: dict[str, float] = {start_node.name: 0.0}

        queue: list[tuple[float, int, Node, list[Node]]] = [
            (0.0, id(start_node), start_node, [start_node])
        ]

        while queue:
            curr_dis, _, curr_node, path = heapq.heappop(queue)

            if curr_node == end_node:
                return path, curr_dis

            if curr_dis > distances.get(curr_node.name, float("inf")):
                continue

            for neighbor in curr_node.get_neighbors():
                step_cost = curr_node.get_step_cost(neighbor)
                dis = curr_dis + step_cost

                if dis < distances.get(neighbor.name, float("inf")):
                    distances[neighbor.name] = dis
                    heapq.heappush(
                        queue, (dis, id(neighbor), neighbor, path + [neighbor])
                    )

        return None

    def get_path_cost(self, path: list[Node]) -> float:
        if not path or len(path) < 2:
            return 0.0

        total_cost = 0.0
        for i in range(len(path) - 1):
            curr_node = path[i]
            next_node = path[i + 1]
            total_cost += curr_node.get_step_cost(next_node)

        return total_cost

    def _set_penalty(self, route: Route) -> None:
        for node in route.nodes[1:-1]:
            node.usage_count += 1

    def find(self, end_node: Node, k: int = 5) -> list[Route]:
        paths = []
        seen_signatures: set[tuple[str, ...]] = set()

        max_attempts = k * 10

        for i in range(max_attempts):
            res = self.find_path_to(end_node)

            if not res:
                break

            nodes, cost = res
            route = Route(id=i, nodes=nodes, cost=cost)

            if route.signature not in seen_signatures:
                seen_signatures.add(route.signature)
                paths.append(route)

            self._set_penalty(route)

            if len(paths) == k:
                break

        self.graph.reset_penalties()
        return paths
