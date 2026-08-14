from .node import Node


class Drone:
    def __init__(
        self,
        id: int,
        hub: Node,
        color: str | None = None
    ):
        self.id = id
        self.hub = hub
        self.color = color

    def go_to(self, other: Node) -> bool:
        if self.hub.is_neighbor(other):
            self.hub.remove_drone(self.id)
            other.add_drone(self.id)
            self.hub = other
