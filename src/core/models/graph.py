from .node import Node, Edge

class Graph:
    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: list[Edge] = []
        self.start_node: Node | None = None
        self.end_node: Node | None = None

    def add_node(self, node: Node, is_start: bool = False, is_end: bool = False) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Duplicate node name: {node.name}")
        
        self._nodes[node.name] = node
        
        if is_start:
            if self.start_node is not None:
                raise ValueError("Multiple start nodes defined")
            self.start_node = node
            
        if is_end:
            if self.end_node is not None:
                raise ValueError("Multiple end nodes defined")
            self.end_node = node

    def add_edge(self, source_name: str, target_name: str, max_capacity: int = 1) -> Edge:
        source = self.get_node(source_name)
        target = self.get_node(target_name)
        
        edge = Edge(source=source, target=target, max_capacity=max_capacity)
        self._edges.append(edge)
        return edge

    def get_node(self, name: str) -> Node:
        if name not in self._nodes:
            raise KeyError(f"Node '{name}' not found in graph")
        return self._nodes[name]

    # def validate(self) -> None:
    #     """Проверка валидности графа перед запуском симулятора."""
    #     if not self.start_node or not self.end_node:
    #         raise ValueError("Graph must have both start_hub and end_hub")
    #     # Здесь также можно запустить BFS/DFS для проверки достижения goal из start