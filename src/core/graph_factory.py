from .models.graph import Graph
from .models.node import Node, NodeMetaData

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
            if conn.source not in graph.nodes:
                raise ValueError(
                    f"Connection references undefined zone: '{conn.source}'"
                )
            if conn.target not in graph.nodes:
                raise ValueError(
                    f"Connection references undefined zone: '{conn.target}'"
                )
            if graph.has_edge(conn.source, conn.target):
                raise ValueError(
                    f"Duplicate connection: "
                    f"'{conn.source}-{conn.target}' "
                    "(a-b and b-a are considered the same connection)"
                )

            graph.add_edge(conn.source, conn.target, conn.max_capacity)

        return graph
