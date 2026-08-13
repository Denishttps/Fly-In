from core.models.graph import Graph
from core.models.node import Node, NodeMetaData


class MapParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines: list[str] = []
        self.graph = Graph()

    def get_lines(self) -> list[str]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.lines = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            self.lines = []
        return self.lines

    def _skip_empty_lines_and_comments(self) -> None:
        self.lines = [line for line in self.lines if not line.startswith("#")]

    def get_drone_count(self) -> int:
        for line in self.lines:
            if line.startswith("nb_drones"):
                return int(line.split(":")[1].strip())
        return -1

    def set_hubs(self) -> None:
        for line in self.lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            
            if key == "start_hub":
                self.graph.add_node(self._create_hub(value.strip()), is_start=True)
            elif key == "end_hub":
                self.graph.add_node(self._create_hub(value.strip()), is_end=True)
            elif key == "hub":
                self.graph.add_node(self._create_hub(value.strip()))

    def _create_hub(self, hub_str: str) -> Node:
        parts = hub_str.split(maxsplit=3)
        name = parts[0]
        x, y = int(parts[1]), int(parts[2])

        metadata_str = parts[3] if len(parts) > 3 else ""
        metadata_dict = self.parse_metadata(metadata_str)
        
        return Node(name, x, y, NodeMetaData(**metadata_dict) if metadata_dict else None)

    @staticmethod
    def parse_metadata(metadata_str: str) -> dict[str, str | int]:
        if not metadata_str or not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            return {}

        result = {}
        content = metadata_str[1:-1].strip()
        for item in content.split():
            if "=" in item:
                k, v = item.split("=", 1)
                result[k] = int(v) if v.isdigit() else v
        return result

    def set_edges(self) -> None:
        for line in self.lines:
            if line.startswith("connection"):
                _, value = line.split(":", 1)
                self.graph.add_edge(*self._create_edge(value.strip()))

    def _create_edge(self, edge_str: str) -> tuple[str, str, int]:
        parts = edge_str.split(maxsplit=1)
        source_name, target_name = parts[0].split("-")
        
        metadata_str = parts[1] if len(parts) > 1 else ""
        metadata = self.parse_metadata(metadata_str)
        max_capacity = int(metadata.get("max_link_capacity", 1))
        
        return source_name, target_name, max_capacity

    def get_graph(self) -> Graph:
        self.get_lines()
        self._skip_empty_lines_and_comments()
        self.set_hubs()
        self.set_edges()
        return self.graph
