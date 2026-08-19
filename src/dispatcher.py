from core.utils.load_map import load_map_from_file
from core.manager import SimulationManager

from core.models.tick_result import TickResult, DroneTickInfo
from core.pathfinding import Dijkstra

from core.utils.init_drones import init_drones
from core.models.graph import Graph

from core.models.drone import Drone
from core.models.route import Route


class Dispatcher:
    def __init__(self, file_path: str) -> None:
        self.count, self.graph = load_map_from_file(file_path)
        self.drones = init_drones(self.count, self.graph)
        self.routes = self._get_routes()

        Dispatcher.assign_routes(self.drones, self.routes)
        self._history: list[TickResult] = []
        self._prev_positions: dict[int, str | None] = {}

    def _get_routes(self) -> list[Route]:
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
        self._run_simulation(max_ticks)
        return self._history

    def print_simulation(self, max_ticks: int = 1000) -> list[TickResult]:
        self._prev_positions = {}
        manager = SimulationManager(self.graph, self.drones)

        while not manager.is_finished and manager.current_tick < max_ticks:
            tick_result = manager.step()
            if tick_result is None:
                continue

            self._history.append(tick_result)

            line = self._format_tick_line(tick_result)
            if line is not None:
                print(line)

        return self._history