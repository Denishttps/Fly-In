from enum import Enum
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
        self.occupants: set[int] = set()
        self.usage_count: int = 0

    def is_available(self) -> bool:
        if self.metadata.zone == ZoneType.BLOCKED:
            return False
        if self.metadata.max_drones == -1:
            return True
        return len(self.occupants) < self.metadata.max_drones

    def add_drone(self, drone_id: int) -> None:
        if not self.is_available():
            raise ValueError(f"Zone '{self.name}' is full or blocked")
        self.occupants.add(drone_id)

    def remove_drone(self, drone_id: int) -> None:
        self.occupants.remove(drone_id)

    def get_neighbors(self) -> list["Node"]:
        return [edge.get_opposite(self) for edge in self.edges]

    def is_neighbor(self, other: "Node") -> bool:
        return other in self.get_neighbors()

    def get_edge_to(self, other: "Node") -> "Edge | None":
        for edge in self.edges:
            if edge.get_opposite(self) == other:
                return edge
        return None

    def get_step_cost(self, target: "Node") -> float:
        edge = self.get_edge_to(target)
        edge_capacity = edge.max_capacity if edge else 999_999

        cap_current = (
            self.metadata.max_drones
            if self.metadata.max_drones != -1 else 999_999
        )
        cap_target = (
            target.metadata.max_drones
            if target.metadata.max_drones != -1 else 999_999
        )
        throughput = min(cap_current, edge_capacity, cap_target)

        k = target.usage_count + 1
        capacity_delay = k / max(throughput, 1)

        return target.base_cost + capacity_delay

    @property
    def base_cost(self) -> float:
        zone = self.metadata.zone
        if zone == ZoneType.BLOCKED:
            return float("inf")
        if zone == ZoneType.RESTRICTED:
            return 2.0
        if zone == ZoneType.PRIORITY:
            return 0.8
        return 1.0

    @property
    def effective_capacity(self) -> int:
        if self.metadata.max_drones == -1:
            return 999_999

        total_link_capacity = sum(e.max_capacity for e in self.edges) or 1
        return min(self.metadata.max_drones, total_link_capacity)

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
