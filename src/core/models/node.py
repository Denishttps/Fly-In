from pydantic import BaseModel

from typing import TYPE_CHECKING
from .zone_type import ZoneType

if TYPE_CHECKING:
    from .edge import Edge


class NodeMetaData(BaseModel):
    color: str | None = None
    max_drones: int = 1
    zone: ZoneType = ZoneType.NORMAL


class Node:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        metadata: NodeMetaData
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.metadata = metadata

        self.edges: list["Edge"] = []

    def get_neighbors(self) -> list["Node"]:
        return [edge.get_opposite(self) for edge in self.edges]

    def is_neighbor(self, other: "Node") -> bool:
        return other in self.get_neighbors()

    def get_edge_to(self, other: "Node") -> "Edge | None":
        for edge in self.edges:
            if edge.get_opposite(self) == other:
                return edge
        return None

    def __repr__(self) -> str:
        zone = self.metadata.zone.value
        drones = self.metadata.max_drones
        drones_str = drones if drones > 0 else float("inf")
        return (
            f"Node(name={self.name!r}, x={self.x}, y={self.y}, "
            f"zone={zone!r}, max_drones={drones_str!r})"
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return self.name == value.name

    def __hash__(self) -> int:
        return hash(self.name)
