from .interfaces import PathFinder
from .models.graph import Graph

import heapq
from .models.node import Node


class Dijkstra(PathFinder):
    def __init__(
        self,
        graph: Graph
    ):
        self.graph = graph

    def find_path_to(self, end_node: Node,) -> list[Node] | None:
        start_node = self.graph.start_node
        distances: dict[str, float] = {start_node.name: 0.0}

        queue: list[tuple[float, int, Node, list[Node]]] = [
            (0.0, id(start_node), start_node, [start_node])
        ]

        while queue:
            curr_dis, _, curr_node, path = heapq.heappop(queue)

            if curr_node == end_node:
                return path

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

    def _set_penalty(self, path: list[Node]) -> None:
        for node in path[1:-1]:
            node.usage_count += 1

    def find(self, end_node: Node, k: int = 5) -> list[list[Node]]:
        paths: list[list[Node]] = []
        seen_signatures: set[tuple[str, ...]] = set()

        max_attempts = k * 10

        for _ in range(max_attempts):
            path = self.find_path_to(end_node)

            if not path:
                break

            signature = tuple(node.name for node in path)

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                paths.append(path)

            self._set_penalty(path)

            if len(paths) == k:
                break

        print(len(paths))
        return paths
