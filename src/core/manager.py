from collections import defaultdict

from .models.graph import Graph
from .models.drone import Drone, MoveRequest

from .models.node import Edge, ZoneType


class SimulationManager:
    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.current_tick: int = 0
        self.current_duty: int = 0
        
    @property
    def is_finished(self) -> bool:
        return all(dr.is_finished for dr in self.drones)
    
    @property
    def total_time(self) -> int:
        return self.current_tick + self.current_duty

    def _intent(self) -> list[MoveRequest]:
        requests = []
        for dr in self.drones:
            req = dr.create_move_request()
            if req:
                requests.append(req)
        return requests

    def _create_request_groups(
        self,
        requests: list[MoveRequest]
    ) -> dict[str, list[MoveRequest]]:
        groups: dict[str, list[MoveRequest]] = defaultdict(list)

        for req in requests:
            groups[req.target_node.name].append(req)

        for v in groups.values():
            v.sort(key=lambda m: (m.priority, -m.drone.id), reverse=True)

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
        
        if req.target_node.metadata.zone == ZoneType.RESTRICTED:
            self.current_duty += 1

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
        if self.is_finished:
            return

        self.current_tick += 1

        requests = self._intent()
        if requests:
            groups = self._create_request_groups(requests)
            self._execute(groups)
            
        tick_output = self._format_tick_output()
        if tick_output:
            print(tick_output)
            
    def _format_tick_output(self) -> str:
        drones_status = []

        for drone in sorted(self.drones, key=lambda d: d.id):
            if not drone.is_finished or getattr(drone, "finished_on_tick", None) == self.current_tick:
                node_name = drone.current_node.name
                drones_status.append(f"D{drone.id}-{node_name}")

        return " ".join(drones_status)

    def run(self, max_ticks: int = 1000) -> None:
        while not self.is_finished and self.current_tick < max_ticks:
            self.step()
            
        print(
            f"Симуляция завершена!\n"
            f"  • Реальных тиков: {self.current_tick}\n"
            f"  • Долг (штрафы):  {self.current_duty}\n"
            f"  • Итоговое время: {self.total_time}"
        )
