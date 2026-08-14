from enum import Enum
from pydantic import BaseModel


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


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

        self.incoming_edges: list["Edge"] = []
        self.outgoing_edges: list["Edge"] = []
        self.occupants: set[int] = set()

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

    def get_neighbors(
        self,
        in_only: bool = False,
        out_only: bool = False
    ) -> list["Node"]:
        if in_only and out_only:
            raise ValueError("Choose either in_only or out_only, not both")

        if out_only:
            edges = self.outgoing_edges
        elif in_only:
            edges = self.incoming_edges
        else:
            edges = self.incoming_edges + self.outgoing_edges

        return [edge.get_opposite(self) for edge in edges]

    def is_neighbor(self, other: "Node") -> bool:
        return other in self.get_neighbors()

    def get_edge_to(self, other: "Node") -> "Edge | None":
        for edge in self.outgoing_edges:
            if edge.target == other:
                return edge
        return None

    def get_edge_between(
        self,
        other: "Node",
        directed: bool = True
    ) -> "Edge | None":
        edge = self.get_edge_to(other)
        if edge is not None:
            return edge

        if not directed:
            for edge in self.incoming_edges:
                if edge.source == other:
                    return edge

        return None

    def __repr__(self) -> str:
        zone = self.metadata.zone.value
        drones = self.metadata.max_drones
        drones_str = drones if drones > 0 else float("inf")
        return (
            f"Node("
            f"name={self.name!r}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"zone={zone!r}, "
            f"max_drones={drones_str!r}"
            f")"
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return (
            self.name == value.name and
            self.x == value.x and
            self.y == value.y and
            self.metadata == value.metadata
        )


class Edge:
    def __init__(
        self,
        source: Node,
        target: Node,
        max_capacity: int = 1
    ) -> None:
        self.source = source
        self.target = target
        self.max_capacity = max_capacity
        self.transits: list[tuple[str, int]] = []

        self.source.outgoing_edges.append(self)
        self.target.incoming_edges.append(self)

    @property
    def travel_cost(self) -> int:
        return 2 if self.target.metadata.zone == ZoneType.RESTRICTED else 1

    def is_available(self, tick: int) -> bool:
        return len(self._reservations[tick]) < self.max_capacity

    def reserve(self, drone_id: int, tick: int) -> bool:
        if not self.is_available(tick):
            return False
        self._reservations[tick].add(drone_id)
        return True

    def cancel_reservation(self, drone_id: int, tick: int) -> None:
        self._reservations[tick].discard(drone_id)

    def cleanup_old_ticks(self, current_tick: int) -> None:
        old_ticks = [t for t in self._reservations if t < current_tick]
        for t in old_ticks:
            del self._reservations[t]

    def get_opposite(self, node: Node) -> Node:
        if node == self.source:
            return self.target
        if node == self.target:
            return self.source
        raise ValueError(f"Node '{node.name}' is not connected to this edge")

    def __repr__(self) -> str:
        return (
            f"Edge(source={self.source.name!r}, "
            f"target={self.target.name!r}, "
            f"max_capacity={self.max_capacity})"
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Edge):
            return False
        return (
            self.source == value.source and
            self.target == value.target and
            self.max_capacity == value.max_capacity
        )