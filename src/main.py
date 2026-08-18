

import sys
from core.utils.load_map import load_map_from_file

from core.pathfinding import Dijkstra

from core.utils.init_drones import init_drones
from core.dispatcher import Dispatcher


def main():
    count, graph = load_map_from_file("/home/dbobrov/Projects/github/Fly-In/maps/hard/03_ultimate_challenge.txt")
    print(graph.start_node)
    print(graph.start_node.get_neighbors())
    dj = Dijkstra(graph)
    routes = dj.find(graph.end_node)
    drones = init_drones(count, graph)
    Dispatcher.assign_routes(drones, routes)
    print([d.route.id for d in drones])



if __name__ == "__main__":
    main()