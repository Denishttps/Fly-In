from dataclasses import dataclass
from .node import Node, Edge


@dataclass
class MoveRequest:
    drone_id: int
    current_node: Node
    target_node: Node
    edge: Edge
    priority: int = 0
