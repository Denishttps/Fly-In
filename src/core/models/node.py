from enum import Enum

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    
    
class NodeMetaData(BaseModel):
    color: str
    max_drones: int = 1
    zone: ZoneType = ZoneType.NORMAL


class Node:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        metadata: NodeMetaData | None = None,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.metadata = metadata

        self.incoming_edges: list["Edge"] = []
        self.outgoing_edges: list["Edge"] = []
        self.occupants: set[str] = set()

    def is_available(self) -> bool:
        if self.metadata.zone == ZoneType.BLOCKED:
            return False
        return len(self.occupants) < self.metadata.max_drones

    def add_drone(self, drone_id: str) -> None:
        if not self.is_available():
            raise ValueError(f"Zone {self.name} is full or blocked")
        self.occupants.add(drone_id)

    def remove_drone(self, drone_id: str) -> None:
        self.occupants.remove(drone_id)

    def __repr__(self) -> str:
        return f"Node({self.name}, type={self.metadata.zone.value})"


class Edge:
    def __init__(self, source: Node, target: Node, max_capacity: int = 1) -> None:
        self.source = source
        self.target = target
        self.max_capacity = max_capacity
        self.transits: list[tuple[str, int]] = []

        self.source.outgoing_edges.append(self)
        self.target.incoming_edges.append(self)

    @property
    def travel_cost(self) -> int:
        return 2 if self.target.type == ZoneType.RESTRICTED else 1

    def is_available(self) -> bool:
        return len(self.transits) < self.max_capacity
