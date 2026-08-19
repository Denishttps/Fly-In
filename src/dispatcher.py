from core.utils.load_map import load_map_from_file
from core.manager import SimulationManager

from core.models.tick_models import TickResult, DroneTickInfo
from core.pathfinding import Dijkstra

from core.models.reservation import ReservationTable
from core.time_expanded_planner import SpaceTimeAStar, DronePlan

from core.utils.init_drones import init_drones

from core.models.drone import Drone
from core.models.route import Route


Strategy = str


class Dispatcher:
    def __init__(self, file_path: str, strategy: Strategy = "time_expanded") -> None:
        self.count, self.graph = load_map_from_file(file_path)
        self.drones = init_drones(self.count, self.graph)
        self.strategy = strategy

        self._history: list[TickResult] = []
        self._prev_positions: dict[int, str | None] = {}

        self.routes: list[Route] = []
        self.plans: dict[int, DronePlan] = {}

        if strategy == "time_expanded":
            self.plans = self._plan_time_expanded()
            self._history = self._build_history_from_plans()
        else:
            self.routes = self._get_routes()
            Dispatcher.assign_routes(self.drones, self.routes)

    def _plan_time_expanded(self) -> dict[int, DronePlan]:
        reservations = ReservationTable()
        planner = SpaceTimeAStar(self.graph, reservations)

        plans: dict[int, DronePlan] = {}
        for drone in sorted(self.drones, key=lambda d: d.id):
            plans[drone.id] = planner.plan(drone.id)

        return plans

    def _build_history_from_plans(self) -> list[TickResult]:
        if not self.plans:
            return []

        makespan = max(plan.makespan for plan in self.plans.values())
        total = len(self.plans)

        history: list[TickResult] = []
        for tick in range(1, makespan + 1):
            infos = [
                self.plans[drone_id].info_at(tick)
                for drone_id in sorted(self.plans)
            ]
            finished = sum(1 for info in infos if info.is_finished)
            history.append(
                TickResult(
                    tick=tick,
                    is_finished=(finished == total),
                    total_time=tick,
                    drones=infos,
                )
            )

        return history

    @property
    def total_turns(self) -> int:
        return self._history[-1].tick if self._history else 0

    @property
    def average_turns_per_drone(self) -> float:
        if not self.plans:
            return 0.0
        return sum(p.makespan for p in self.plans.values()) / len(self.plans)

    def _get_routes(self) -> list[Route]:
        if self.graph.end_node is None:
            raise ValueError("Graph has no end zone defined.")
        dj = Dijkstra(self.graph)
        return dj.find(self.graph.end_node)

    @staticmethod
    def assign_routes(drones: list[Drone], routes: list[Route]) -> None:
        if not routes:
            raise ValueError("List of routes is empty.")

        node_load: dict[str, int] = {}
        route_usage = [0] * len(routes)

        for drone in drones:
            best_route_idx = 0
            best_eta = float("inf")

            for idx, route in enumerate(routes):
                shared_names = route.node_names
                if shared_names:
                    current_load = max(
                        node_load.get(name, 0) for name in shared_names
                    )
                else:
                    current_load = 0

                queue_delay = current_load // route.bottleneck_capacity
                estimated_arrival = queue_delay + route.length

                if estimated_arrival < best_eta:
                    best_eta = estimated_arrival
                    best_route_idx = idx

            chosen_route = routes[best_route_idx]
            drone.assign_route(chosen_route)

            route_usage[best_route_idx] += 1
            for name in chosen_route.node_names:
                node_load[name] = node_load.get(name, 0) + 1

    @staticmethod
    def _location_token(info: DroneTickInfo) -> str | None:
        if info.connection_name is not None:
            return info.connection_name
        return info.node_name

    def _format_tick_line(self, tick: TickResult) -> str | None:
        moves = []

        for info in tick.drones:
            token = self._location_token(info)
            if token is None:
                continue

            prev = self._prev_positions.get(info.drone_id)
            if token != prev:
                moves.append(f"D{info.drone_id}-{token}")

            self._prev_positions[info.drone_id] = token

        if not moves:
            return None

        return " ".join(moves)

    def _run_simulation(self, max_ticks: int = 1000) -> None:
        manager = SimulationManager(self.graph, self.drones)
        while not manager.is_finished and manager.current_tick < max_ticks:
            tick_result = manager.step()
            if tick_result is not None:
                self._history.append(tick_result)

    def compute_all(self, max_ticks: int = 1000) -> list[TickResult]:
        if self.strategy == "time_expanded":
            return self._history
        self._run_simulation(max_ticks)
        return self._history

    def print_simulation(self, max_ticks: int = 1000) -> list[TickResult]:
        self._prev_positions = {}

        if self.strategy == "time_expanded":
            for tick_result in self._history:
                line = self._format_tick_line(tick_result)
                if line is not None:
                    print(line)
            return self._history

        manager = SimulationManager(self.graph, self.drones)
        while not manager.is_finished and manager.current_tick < max_ticks:
            step_result: TickResult | None = manager.step()
            if step_result is None:
                continue

            self._history.append(step_result)

            line = self._format_tick_line(step_result)
            if line is not None:
                print(line)

        return self._history
