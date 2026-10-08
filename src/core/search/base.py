import heapq
from abc import ABC, abstractmethod

from ..models.graph import Graph
from ..models.zone_type import ZoneType
from ..models.reservation import ReservationTable


State = tuple[str, int]
CameFrom = dict[State, tuple[State, str, str | None]]


class SpaceTimeSearch(ABC):
    def __init__(self, graph: Graph, reservations: ReservationTable) -> None:
        self.graph = graph
        self.reservations = reservations

    @abstractmethod
    def _priority(self, node_name: str, g: float) -> float:
        ...

    def cost_lower_bound(self, node_name: str) -> float:
        return 0.0

    def _is_priority(self, node_name: str) -> bool:
        return (
            self.graph.get_node(node_name).metadata.zone == ZoneType.PRIORITY
        )

    def search(
        self,
        start_name: str,
        goal_name: str,
        start_tick: int,
        horizon: int,
    ) -> tuple[CameFrom, State | None]:
        deadline = start_tick + horizon

        g_score: dict[State, float] = {(start_name, start_tick): 0.0}
        came_from: CameFrom = {}
        closed: set[State] = set()

        counter = 0
        open_heap: list[tuple[float, int, int, str, int]] = [
            (
                self._priority(start_name, 0.0),
                0,
                counter,
                start_name,
                start_tick,
            )
        ]
        best_np: dict[State, int] = {(start_name, start_tick): 0}

        while open_heap:
            _, np_count, _, node_name, tick = heapq.heappop(open_heap)
            state: State = (node_name, tick)
            g = g_score[state]

            if state in closed:
                continue
            closed.add(state)

            if node_name == goal_name:
                return came_from, state

            if tick >= deadline:
                continue

            node = self.graph.get_node(node_name)

            if self.reservations.is_node_free(node, tick + 1):
                wait_state: State = (node_name, tick + 1)
                wait_g = g + 1.0
                if wait_state not in closed and (
                    wait_g < g_score.get(wait_state, float("inf"))
                    or (
                        wait_g == g_score.get(wait_state, float("inf"))
                        and np_count < best_np.get(wait_state, float("inf"))
                    )
                ):
                    g_score[wait_state] = wait_g
                    best_np[wait_state] = np_count
                    came_from[wait_state] = (state, "wait", None)
                    counter += 1
                    heapq.heappush(
                        open_heap,
                        (
                            self._priority(node_name, wait_g),
                            np_count,
                            counter,
                            node_name,
                            tick + 1,
                        ),
                    )

            for neighbor in node.get_neighbors():
                if neighbor.metadata.zone == ZoneType.BLOCKED:
                    continue

                edge = node.get_edge_to(neighbor)
                if edge is None:
                    continue

                duration = (
                    2 if neighbor.metadata.zone == ZoneType.RESTRICTED else 1
                )
                arrival_tick = tick + duration
                if arrival_tick > deadline:
                    continue

                if not self.reservations.is_edge_free(
                    edge, tick + 1, 1
                ):
                    continue
                if not self.reservations.is_node_free(neighbor, arrival_tick):
                    continue

                move_state: State = (neighbor.name, arrival_tick)
                if move_state in closed:
                    continue

                move_g = g + duration
                move_np = np_count + (
                    0 if self._is_priority(neighbor.name) else 1
                )
                if move_g < g_score.get(move_state, float("inf")) or (
                    move_g == g_score.get(move_state, float("inf"))
                    and move_np < best_np.get(move_state, float("inf"))
                ):
                    g_score[move_state] = move_g
                    best_np[move_state] = move_np
                    came_from[move_state] = (
                        state, "move", f"{node.name}-{neighbor.name}"
                    )
                    counter += 1
                    heapq.heappush(
                        open_heap,
                        (
                            self._priority(neighbor.name, move_g),
                            move_np,
                            counter,
                            neighbor.name,
                            arrival_tick,
                        ),
                    )

        return came_from, None
