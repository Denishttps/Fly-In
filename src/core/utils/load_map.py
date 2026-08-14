from core.models.graph import Graph
from core.parser import MapTextParser

from core.graph_factory import GraphFactory


def load_map_from_file(file_path: str) -> tuple[int, Graph]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    data = MapTextParser.parse_text(content)
    graph = GraphFactory.build_graph(data.hubs, data.connections)

    return data.drone_count, graph
