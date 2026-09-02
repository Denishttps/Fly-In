from app.schemas.tick import TickResultDTO
from core.models import Node, Edge

from ..schemas.graph import EdgeDTO, GraphDTO, NodeDTO
from ..schemas.response import SimulationResponse

from dispatcher import Dispatcher
from pathlib import Path

from ..schemas.file import FileDTO

from typing import ClassVar


class SimulationService:
    PRIORITY: ClassVar[dict[str, int]] = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "challenger": 4
        }

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

    def get_all_maps(self) -> list[FileDTO]:
        base_path = "maps"
        path = Path(base_path)

        files: list[FileDTO] = []

        for file in path.rglob("*"):
            if not file.is_file() or not file.name.endswith(".txt"):
                continue
            files.append(
                FileDTO(
                    name=file.name,
                    group=file.parent.name,
                    path=file.as_posix()
                )
            )

        return sorted(
            files,
            key=lambda f: (self.PRIORITY.get(f.group, 99), f.name)
        )

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
