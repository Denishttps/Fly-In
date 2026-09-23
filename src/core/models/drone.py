from dataclasses import dataclass
from .node import Node


@dataclass
class Drone:
    id: int
    node: Node
