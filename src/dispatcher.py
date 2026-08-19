from core.utils.load_map import load_map_from_file
from core.manager import SimulationManager

from core.models.tick_result import TickResult
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

    def _get_routes(self) -> list[Route]:
        dj = Dijkstra(self.graph)
        return dj.find(self.graph.end_node)
        
    @staticmethod
    def assign_routes(drones: list[Drone], routes: list[Route]) -> None:
        if not routes:
            raise ValueError("List of routes is empty.")

        route_usage = [0] * len(routes)

        for drone in drones:
            best_route_idx = 0
            best_eta = float("inf")

            for idx, route in enumerate(routes):
                drones_count = route_usage[idx]

                queue_delay = drones_count // route.bottleneck_capacity

                estimated_arrival = queue_delay + route.length

                if estimated_arrival < best_eta:
                    best_eta = estimated_arrival
                    best_route_idx = idx

            chosen_route = routes[best_route_idx]
            drone.assign_route(chosen_route)

            route_usage[best_route_idx] += 1
            
    def _run_simulation(self, max_ticks: int = 1000) -> None:
        manager = SimulationManager(self.graph, self.drones)
        while not manager.is_finished and manager.current_tick < max_ticks:
            tick_result = manager.step()
            if tick_result is not None:
                self._history.append(tick_result)
                
    def compute_all(self, max_ticks: int = 1000) -> list[TickResult]:
        self._run_simulation(max_ticks)
        return self._history
        
