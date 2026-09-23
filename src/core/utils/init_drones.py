from ..models.graph import Graph
from ..models.drone import Drone


def init_drones(count: int, graph: Graph) -> list[Drone]:
    drones = []
    for i in range(count):
        drone = Drone(i + 1, graph.start_node)  # type: ignore[arg-type]
        drones.append(drone)
    return drones
