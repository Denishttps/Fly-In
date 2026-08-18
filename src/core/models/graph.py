from .node import Node, Edge


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.start_node: Node | None = None
        self.end_node: Node | None = None

    def add_node(
            self,
            node: Node,
            is_start: bool = False,
            is_end: bool = False
    ) -> None:
        if node.name in self.nodes:
            raise ValueError(f"Duplicate node name: {node.name}")

        self.nodes[node.name] = node

        if is_start:
            if self.start_node is not None:
                raise ValueError("Multiple start nodes defined")
            self.start_node = node

        if is_end:
            if self.end_node is not None:
                raise ValueError("Multiple end nodes defined")
            self.end_node = node

    def add_edge(
            self,
            source_name: str,
            target_name: str,
            max_capacity: int = 1
    ) -> Edge:
        source = self.get_node(source_name)
        target = self.get_node(target_name)

        edge = Edge(source=source, target=target, max_capacity=max_capacity)
        self.edges.append(edge)
        return edge

    def get_node(self, name: str) -> Node:
        if name not in self.nodes:
            raise KeyError(f"Node '{name}' not found in graph")
        return self.nodes[name]

    def reset_penalties(self) -> None:
        for node in self.nodes.values():
            node.usage_count = 0

    def __repr__(self) -> str:
        start = self.start_node.name if self.start_node else None
        end = self.end_node.name if self.end_node else None
        return (
            f"Graph(nodes={len(self.nodes)}, "
            f"edges={len(self.edges)}, "
            f"start={start!r}, "
            f"end={end!r})"
        )

    def __getitem__(self, key: str) -> Node:
        return self.get_node(key)
