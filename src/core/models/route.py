from dataclasses import dataclass
from .node import Node


@dataclass
class Route:
    id: int
    nodes: list[Node]
    cost: float = 0.0

    @property
    def length(self) -> int:
        return len(self.nodes) - 1 if self.nodes else 0

    @property
    def signature(self) -> tuple[str, ...]:
        return tuple(node.name for node in self.nodes)

    def contains(self, node_name: str) -> bool:
        return any(n.name == node_name for n in self.nodes)

    @property
    def node_names(self) -> frozenset[str]:
        if len(self.nodes) <= 2:
            return frozenset()
        return frozenset(n.name for n in self.nodes[1:-1])

    @property
    def bottleneck_capacity(self) -> int:
        if len(self.nodes) < 2:
            return 1

        capacities = []
        for i in range(len(self.nodes) - 1):
            curr_n = self.nodes[i]
            next_n = self.nodes[i + 1]
            edge = curr_n.get_edge_to(next_n)

            c_curr = (
                curr_n.metadata.max_drones
                if curr_n.metadata.max_drones != -1 else 999_999
            )
            c_next = (
                next_n.metadata.max_drones
                if next_n.metadata.max_drones != -1 else 999_999
            )
            c_edge = edge.max_capacity if edge else 999_999

            capacities.append(min(c_curr, c_next, c_edge))

        return max(min(capacities), 1)

    def __repr__(self) -> str:
        nodes_str = " -> ".join(n.name for n in self.nodes)
        return (
            f"Route(cost={self.cost:.2f}, steps={self.length}, [{nodes_str}])"
        )
