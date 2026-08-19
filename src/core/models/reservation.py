from dataclasses import dataclass, field

from .edge import Edge
from .node import Node


UNLIMITED = 999_999


@dataclass
class ReservationTable:
    _node_occupancy: dict[tuple[str, int], int] = field(default_factory=dict)
    _edge_occupancy: dict[tuple[frozenset[str], int], int] = field(
        default_factory=dict
    )

    @staticmethod
    def _node_capacity(node: Node) -> int:
        if node.metadata.max_drones == -1:
            return UNLIMITED
        return node.metadata.max_drones

    @staticmethod
    def _edge_key(edge: Edge) -> frozenset[str]:
        return frozenset({edge.source.name, edge.target.name})

    def node_load(self, node: Node, tick: int) -> int:
        return self._node_occupancy.get((node.name, tick), 0)

    def is_node_free(self, node: Node, tick: int) -> bool:
        from .node import ZoneType  # local import: avoid a cycle

        if node.metadata.zone == ZoneType.BLOCKED:
            return False
        return self.node_load(node, tick) < self._node_capacity(node)

    def reserve_node(self, node: Node, tick: int) -> None:
        key = (node.name, tick)
        self._node_occupancy[key] = self._node_occupancy.get(key, 0) + 1

    def edge_load(self, edge: Edge, tick: int) -> int:
        return self._edge_occupancy.get((self._edge_key(edge), tick), 0)

    def is_edge_free(self, edge: Edge, start_tick: int, duration: int) -> bool:
        for t in range(start_tick, start_tick + duration):
            if self.edge_load(edge, t) >= edge.max_capacity:
                return False
        return True

    def reserve_edge(self, edge: Edge, start_tick: int, duration: int) -> None:
        key_base = self._edge_key(edge)
        for t in range(start_tick, start_tick + duration):
            key = (key_base, t)
            self._edge_occupancy[key] = self._edge_occupancy.get(key, 0) + 1
