from dataclasses import dataclass

from .node import Node, Edge
from .route import Route


@dataclass
class MoveRequest:
    drone: "Drone"
    current_node: Node
    target_node: Node
    edge: Edge
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

    def assign_route(self, route: Route) -> None:
        self.route = route
        self.route_idx = 0
        self.wait_ticks = 0
        self.is_finished = False

        self.current_node = route.nodes[0]
        self.current_node.add_drone(self.id)

    @property
    def next_node(self) -> Node | None:
        if not self.route or self.route_idx + 1 >= len(self.route.nodes):
            return None
        return self.route.nodes[self.route_idx + 1]

    def create_move_request(self) -> "MoveRequest | None":
        if self.is_finished or self.next_node is None:
            return None

        target = self.next_node
        edge = self.current_node.get_edge_to(target)

        priority = float(self.wait_ticks)

        return MoveRequest(
            drone=self,
            current_node=self.current_node,
            target_node=target,
            edge=edge,
            priority=priority
        )

    def move_to(self, target: Node) -> None:
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
        status = (
            "FINISHED" if self.is_finished else f"at {self.current_node.name}"
        )
        return f"Drone(id={self.id}, {status})"
