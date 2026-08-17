from ..models.graph import Graph
from ..models.drone import Drone


def init_drones(count: int, graph: Graph) -> None:
    drones = []
    for i in range(count):
        drone = Drone(i)
