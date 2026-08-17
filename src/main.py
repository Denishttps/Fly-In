

import sys
from core.utils.load_map import load_map_from_file

from core.pathfinding import Dijkstra


def main():
    count, graph = load_map_from_file("/home/dbobrov/Projects/github/Fly-In/maps/hard/03_ultimate_challenge.txt")
    print(graph.start_node)
    print(graph.start_node.get_neighbors())
    dj = Dijkstra(graph)
    paths = dj.find(graph.end_node, k = 10)
    for p in paths:
        print([n.name for n in p])


if __name__ == "__main__":
    main()