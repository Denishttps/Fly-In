from abc import ABC
from .models.node import Node

from .models.graph import Graph


class PathFinder(ABC):
    def __init__(self, graph: Graph):
        self.graph = graph

    def find(self) -> list[Node]:
        ...
