from collections import defaultdict

from .models.graph import Graph
from .models.drone import Drone, MoveRequest

from .models.node import Edge


class SimulationManager:
    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.current_tick: int = 0
        self.current_duty: int = 0

    def _intent(self) -> list[MoveRequest]:
        requests = []
        for dr in self.drones:
            req = dr.create_move_request()
            if req:
                requests.append(req)
        return requests

    def _create_request_groups(
        requests: list[MoveRequest]
    ) -> dict[str, list[MoveRequest]]:
        groups: dict[str, list[MoveRequest]] = defaultdict(list)

        for req in requests:
            groups[req.target_node.name].append(req)

        for v in groups.values():
            v.sort(key=lambda m: (m.priority, -m.drone), reverse=True)

        return groups

    def _execute(self, groups: dict[str, list["MoveRequest"]]) -> None:
        executed_drones: set[int] = set()
        edge_usage: dict[Edge, int] = defaultdict(int)

        while True:
            moved_in_this_pass = False

            for req_list in groups.values():
                for req in req_list:
                    if req.drone.id in executed_drones:
                        continue

                    if self._can_traverse(req, edge_usage):
                        self._apply_move(req, edge_usage, executed_drones)
                        moved_in_this_pass = True
                    else:
                        break

            if not moved_in_this_pass:
                break

        self._penalize_waiting(groups, executed_drones)

    def _can_traverse(
        self,
        req: MoveRequest,
        edge_usage: dict[Edge, int]
    ) -> bool:
        node_has_space = req.target_node.is_available()
        edge_has_space = (
            req.edge is None or edge_usage[req.edge] < req.edge.max_capacity
        )
        return node_has_space and edge_has_space

    def _apply_move(
        self,
        req: MoveRequest,
        edge_usage: dict[Edge, int],
        executed_drones: set[int]
    ) -> None:
        req.drone.move_to(req.target_node)
        if req.edge:
            edge_usage[req.edge] += 1
        executed_drones.add(req.drone.id)

    def _penalize_waiting(
        self,
        groups: dict[str, list[MoveRequest]],
        executed_drones: set[int]
    ) -> None:
        for req_list in groups.values():
            for req in req_list:
                if req.drone.id not in executed_drones:
                    req.drone.wait()

    def step(self) -> None:
        pass
