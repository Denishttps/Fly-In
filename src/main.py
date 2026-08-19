

import sys
from core.manager import SimulationManager
from core.utils.load_map import load_map_from_file

from core.pathfinding import Dijkstra

from core.utils.init_drones import init_drones
from core.dispatcher import Dispatcher


def main():
    count, graph = load_map_from_file("maps/hard/02_capacity_hell.txt")
    dj = Dijkstra(graph)
    routes = dj.find(graph.end_node)
    drones = init_drones(count, graph)
    Dispatcher.assign_routes(drones, routes)
    manager = SimulationManager(graph, drones)
    manager.run()



if __name__ == "__main__":
    main()