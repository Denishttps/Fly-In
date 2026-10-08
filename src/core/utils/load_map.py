from pathlib import Path

from ..models.graph import Graph
from ..parser import MapTextParser

from ..graph_factory import GraphFactory
from ..errors import ParseError


class MapLoader:
    @staticmethod
    def load_map_from_file(file_path: str) -> tuple[int, Graph]:
        path = Path(file_path)
        if path.is_dir():
            raise ParseError(0, f"path '{file_path}' is a directory")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        data = MapTextParser.parse_text(content)
        graph = GraphFactory.build_graph(data.hubs, data.connections)

        return data.drone_count, graph
