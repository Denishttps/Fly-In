import heapq

from ..models.graph import Graph
from ..models.node import Node

from ..models.zone_type import ZoneType


def compute_goal_distances(graph: Graph) -> dict[str, float]:
    end_node = graph.end_node
    if end_node is None:
        raise ValueError("Graph has no end zone defined.")

    dist: dict[str, float] = {end_node.name: 0.0}
    visited: set[str] = set()

    heap: list[tuple[float, int, Node]] = [(0.0, id(end_node), end_node)]

    while heap:
        d, _, node = heapq.heappop(heap)
        if node.name in visited:
            continue
        visited.add(node.name)

        for neighbor in node.get_neighbors():
            if neighbor.metadata.zone == ZoneType.BLOCKED:
                continue

            step = (
                2.0 if neighbor.metadata.zone == ZoneType.RESTRICTED else 1.0
            )
            nd = d + step

            if nd < dist.get(neighbor.name, float("inf")):
                dist[neighbor.name] = nd
                heapq.heappush(heap, (nd, id(neighbor), neighbor))

    return dist
