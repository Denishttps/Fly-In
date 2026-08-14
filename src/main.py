

import sys
from core.utils.load_map import load_map_from_file


def main():
    count, graph = load_map_from_file("/home/dbobrov/Projects/github/Fly-In/maps/hard/03_ultimate_challenge.txt")
    print(graph.start_node)
    print(graph.get_neigbors(graph.start_node))


if __name__ == "__main__":
    main()