from .base import SpaceTimeSearch


class DijkstraSearch(SpaceTimeSearch):
    def _priority(self, node_name: str, g: float) -> float:
        return g
