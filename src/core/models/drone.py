from dataclasses import dataclass

from .node import Node, Edge, ZoneType
from .route import Route


@dataclass
class MoveRequest:
    drone: "Drone"
    current_node: Node
    target_node: Node
    edge: Edge | None
    travel_ticks: int
    priority: int = 0


class Drone:
    def __init__(
        self,
        id: int,
        start_node: Node,
        color: str | None = None
    ) -> None:
        self.id = id
        self.color = color

        self.route: Route | None = None
        self.route_idx: int = 0
        self.wait_ticks: int = 0
        self.is_finished: bool = False

        self.current_node: Node = start_node

        # Transit state: set when a multi-tick move (e.g. into a
        # restricted zone) has been committed. While in transit the
        # drone occupies neither current_node nor target_node in the
        # zone-capacity sense — only the edge/connection.
        self.transit_edge: Edge | None = None
        self.transit_target: Node | None = None
        self.transit_ticks_remaining: int = 0

    @property
    def in_transit(self) -> bool:
        return self.transit_edge is not None

    def assign_route(self, route: Route) -> None:
        self.route = route
        self.route_idx = 0
        self.wait_ticks = 0
        self.is_finished = False

        self.transit_edge = None
        self.transit_target = None
        self.transit_ticks_remaining = 0

        self.current_node = route.nodes[0]
        self.current_node.add_drone(self.id)

    @property
    def next_node(self) -> Node | None:
        if not self.route or self.route_idx + 1 >= len(self.route.nodes):
            return None
        return self.route.nodes[self.route_idx + 1]

    def create_move_request(self) -> "MoveRequest | None":
        # A drone already committed to a multi-tick transit cannot
        # issue a new request; it must be advanced via advance_transit().
        if self.is_finished or self.in_transit or self.next_node is None:
            return None

        target = self.next_node
        edge = self.current_node.get_edge_to(target)

        travel_ticks = edge.travel_cost if edge else 1

        priority = float(self.wait_ticks)

        return MoveRequest(
            drone=self,
            current_node=self.current_node,
            target_node=target,
            edge=edge,
            travel_ticks=travel_ticks,
            priority=priority
        )

    def start_transit(self, req: "MoveRequest") -> None:
        """Commit to a move that takes more than one tick (e.g. into
        a restricted zone). The drone leaves current_node immediately
        and occupies the connection until arrival; it cannot be
        interrupted or made to wait mid-transit.
        """
        self.current_node.remove_drone(self.id)
        self.current_node = None  # type: ignore[assignment]

        self.transit_edge = req.edge
        self.transit_target = req.target_node
        self.transit_ticks_remaining = req.travel_ticks - 1
        self.wait_ticks = 0

    def advance_transit(self) -> bool:
        """Advance an in-progress multi-tick move by one tick.
        Returns True if the drone has now arrived (caller must still
        occupy the target node's capacity before calling this).
        """
        self.transit_ticks_remaining -= 1
        return self.transit_ticks_remaining <= 0

    def complete_transit(self) -> None:
        target = self.transit_target
        assert target is not None

        target.add_drone(self.id)
        self.current_node = target
        self.route_idx += 1

        self.transit_edge = None
        self.transit_target = None
        self.transit_ticks_remaining = 0

        if self.route and self.route_idx == len(self.route.nodes) - 1:
            self.is_finished = True

    def move_to(self, target: Node) -> None:
        """Instant (single-tick) move — used for normal/priority
        zones where travel_cost == 1.
        """
        self.current_node.remove_drone(self.id)
        target.add_drone(self.id)

        self.current_node = target
        self.route_idx += 1
        self.wait_ticks = 0

        if self.route and self.route_idx == len(self.route.nodes) - 1:
            self.is_finished = True

    def wait(self) -> None:
        self.wait_ticks += 1

    def __repr__(self) -> str:
        if self.in_transit and self.transit_edge is not None:
            status = (
                f"in transit on {self.transit_edge!r} "
                f"({self.transit_ticks_remaining} ticks left)"
            )
        elif self.is_finished:
            status = "FINISHED"
        else:
            status = f"at {self.current_node.name}"
        return f"Drone(id={self.id}, {status})"