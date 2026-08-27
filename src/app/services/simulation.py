from app.schemas.tick import TickResultDTO
from core.models import Node, Edge

from ..schemas.graph import EdgeDTO, GraphDTO, NodeDTO
from dispatcher import Dispatcher

from ..schemas.response import SimulationResponse
from pathlib import Path


class SimulationService:
    def get_simulation(self, path: str) -> SimulationResponse:
        dp = Dispatcher(path)
        self.graph = dp.graph
        self.history = dp.compute_all()

        graph_read = self._create_graph()
        history_read = self._create_history()

        return SimulationResponse(
            graph=graph_read,
            history=history_read
        )

    def get_all_maps(self) -> list[str]:
        base_path = "maps"
        path = Path(base_path)

        files = [
            (file.name, file.as_posix()) for file in path.rglob("*")
            if file.is_file() and str(file).endswith(".txt")
        ]
        return files

    def _create_nodes(self, nodes: dict[str, Node]) -> list[NodeDTO]:
        result = []

        for _, nd in nodes.items():
            result.append(
                NodeDTO.model_validate(nd)
            )

        return result

    def _create_edges(self, edges: list[Edge]) -> list[EdgeDTO]:
        result = []

        for ed in edges:
            result.append(
                EdgeDTO.model_validate(ed)
            )

        return result

    def _create_graph(self) -> GraphDTO:
        nodes = self._create_nodes(self.graph.nodes)
        edges = self._create_edges(self.graph.edges)

        return GraphDTO(
            edges=edges,
            nodes=nodes
        )

    def _create_history(self) -> list[TickResultDTO]:
        result = []

        for tick in self.history:
            result.append(
                TickResultDTO.model_validate(tick)
            )

        return result
