from core.models.graph import Graph
from core.models.node import Node, NodeMetaData

from .models.map import RawHub, RawConnection


class GraphFactory:
    @staticmethod
    def build_graph(
        hubs: list[RawHub],
        connections: list[RawConnection]
    ) -> Graph:
        graph = Graph()

        for hub in hubs:
            metadata = dict(hub.metadata)
            if hub.is_start or hub.is_end:
                metadata["max_drones"] = -1

            node = Node(
                hub.name,
                hub.x,
                hub.y,
                NodeMetaData(**metadata)
            )
            graph.add_node(node, is_start=hub.is_start, is_end=hub.is_end)

        for conn in connections:
            graph.add_edge(conn.source, conn.target, conn.max_capacity)

        return graph
