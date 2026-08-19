from typing import TYPE_CHECKING
from core.models.zone_type import ZoneType

if TYPE_CHECKING:
    from .node import Node


class Edge:
    def __init__(
        self,
        source: "Node",
        target: "Node",
        max_capacity: int = 1
    ) -> None:
        self.source = source
        self.target = target
        self.max_capacity = max_capacity

        self.source.edges.append(self)
        self.target.edges.append(self)

    @property
    def travel_cost(self) -> int:
        return 2 if self.target.metadata.zone == ZoneType.RESTRICTED else 1

    def get_opposite(self, node: "Node") -> "Node":
        if node == self.source:
            return self.target
        if node == self.target:
            return self.source
        raise ValueError(f"Node '{node.name}' is not connected to this edge")

    def __repr__(self) -> str:
        return (
            f"Edge(source={self.source.name!r}, target={self.target.name!r}, "
            f"max_capacity={self.max_capacity})"
        )

    def __eq__(self, value: "Edge") -> bool:
        if not isinstance(value, Edge):
            return False
        return (
            self.source == value.source and self.target == value.target
        ) or (
            self.source == value.target and self.target == value.source
        )

    def __hash__(self) -> int:
        return hash(frozenset({self.source.name, self.target.name}))
