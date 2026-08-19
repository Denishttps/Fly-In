from collections import defaultdict

from .models.graph import Graph, Edge
from .models.drone import Drone, MoveRequest

from .models.tick_result import DroneTickInfo, TickResult


class SimulationManager:
    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.current_tick: int = 0

    @property
    def is_finished(self) -> bool:
        return all(dr.is_finished for dr in self.drones)

    @property
    def total_time(self) -> int:
        return self.current_tick

    def _intent(self) -> list[MoveRequest]:
        requests = []
        for dr in self.drones:
            req = dr.create_move_request()
            if req:
                requests.append(req)
        return requests

    def _create_request_groups(
        self, requests: list[MoveRequest]
    ) -> dict[str, list[MoveRequest]]:
        groups: dict[str, list[MoveRequest]] = defaultdict(list)

        for req in requests:
            groups[req.target_node.name].append(req)

        for v in groups.values():
            v.sort(key=lambda m: (m.priority, -m.drone.id), reverse=True)

        return groups

    def _advance_transits(self) -> None:
        for dr in self.drones:
            if not dr.in_transit:
                continue
            if dr.advance_transit():
                dr.complete_transit()

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

    def _can_traverse(self, req: MoveRequest, edge_usage: dict[Edge, int]) -> bool:
        node_has_space = req.target_node.is_available()
        edge_has_space = (
            req.edge is None or edge_usage[req.edge] < req.edge.max_capacity
        )
        return node_has_space and edge_has_space

    def _apply_move(
        self, req: MoveRequest, edge_usage: dict[Edge, int], executed_drones: set[int]
    ) -> None:
        if req.edge:
            edge_usage[req.edge] += 1

        executed_drones.add(req.drone.id)

        if req.travel_ticks > 1:
            req.drone.start_transit(req)
        else:
            req.drone.move_to(req.target_node)

    def _penalize_waiting(
        self, groups: dict[str, list[MoveRequest]], executed_drones: set[int]
    ) -> None:
        for req_list in groups.values():
            for req in req_list:
                if req.drone.id not in executed_drones:
                    req.drone.wait()

    def _get_drone_statuses(self) -> list[DroneTickInfo]:
        statuses = []
        for drone in sorted(self.drones, key=lambda d: d.id):
            if drone.in_transit and drone.transit_edge is not None:
                statuses.append(DroneTickInfo(
                    drone_id=drone.id,
                    node_name=None,
                    connection_name=(
                        f"{drone.transit_edge.source.name}"
                        f"_{drone.transit_edge.target.name}"
                    ),
                    is_finished=False
                ))
            else:
                statuses.append(DroneTickInfo(
                    drone_id=drone.id,
                    node_name=drone.current_node.name,
                    connection_name=None,
                    is_finished=drone.is_finished
                ))
        return statuses

    def step(self) -> TickResult | None:
        if self.is_finished:
            return None

        self.current_tick += 1

        self._advance_transits()

        requests = self._intent()
        if requests:
            groups = self._create_request_groups(requests)
            self._execute(groups)

        return TickResult(
            tick=self.current_tick,
            is_finished=self.is_finished,
            total_time=self.total_time,
            drones=self._get_drone_statuses()
        )