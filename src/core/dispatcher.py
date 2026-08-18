from .models.drone import Drone
from .models.route import Route


class Dispatcher:
    @staticmethod
    def assign_routes(drones: list[Drone], routes: list[Route]) -> None:
        if not routes:
            raise ValueError("Список маршрутов пуст!")

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
