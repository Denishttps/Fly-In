from ..models.graph import Graph
from ..models.reservation import ReservationTable

from ..utils.distances import compute_goal_distances
from .base import SpaceTimeSearch


class AStarSearch(SpaceTimeSearch):
    """A*: priority = g + shortest-path distance to the goal zone."""

    def __init__(self, graph: Graph, reservations: ReservationTable) -> None:
        super().__init__(graph, reservations)
        self._goal_dist = compute_goal_distances(graph)

    def heuristic(self, node_name: str) -> float:
        return self._goal_dist.get(node_name, float("inf"))

    def cost_lower_bound(self, node_name: str) -> float:
        return self.heuristic(node_name)

    def _priority(self, node_name: str, g: float) -> float:
        return g + self.heuristic(node_name)
