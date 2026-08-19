import heapq

from .models.graph import Graph
from .models.node import Node, ZoneType

from .models.reservation import ReservationTable
from .models.tick_models import DronePlan, PlannedStep

from .utils.distances import compute_goal_distances
from .time_errors import NoPlanFoundError


State = tuple[str, int]
CameFrom = dict[State, tuple[State, str, str | None]]


class SpaceTimeAStar:
    def __init__(self, graph: Graph, reservations: ReservationTable) -> None:
        self.graph = graph
        self.reservations = reservations
        self._goal_dist = compute_goal_distances(graph)

    def plan(
        self,
        drone_id: int,
        start_tick: int = 0,
        horizon_padding: int = 40,
        max_horizon: int = 4000,
    ) -> DronePlan:
        start = self.graph.start_node
        goal = self.graph.end_node
        if start is None or goal is None:
            raise ValueError("Graph must have both a start zone and an end zone.")

        if start.name == goal.name:
            return DronePlan(drone_id=drone_id, end_node_name=goal.name)

        h0 = self._goal_dist.get(start.name, float("inf"))
        if h0 == float("inf"):
            raise NoPlanFoundError(
                f"No path exists from '{start.name}' to '{goal.name}'."
            )

        horizon = int(h0) + horizon_padding
        while horizon <= max_horizon:
            came_from, goal_state = self._search(start, goal, start_tick, horizon)
            if goal_state is not None:
                return self._commit_and_build(
                    drone_id, came_from, goal_state, goal
                )
            horizon *= 2

        raise NoPlanFoundError(
            f"Drone D{drone_id}: no conflict-free path to '{goal.name}' "
            f"found within {max_horizon} ticks — the network may be "
            "deadlocked by capacity constraints."
        )

    def _search(
        self,
        start: Node,
        goal: Node,
        start_tick: int,
        horizon: int,
    ) -> tuple[CameFrom, State | None]:
        deadline = start_tick + horizon

        g_score: dict[State, float] = {(start.name, start_tick): 0.0}
        came_from: CameFrom = {}
        closed: set[State] = set()

        counter = 0
        open_heap: list[tuple[float, float, int, str, int]] = [
            (
                self._goal_dist.get(start.name, float("inf")),
                0.0,
                counter,
                start.name,
                start_tick,
            )
        ]

        while open_heap:
            _, g, _, node_name, tick = heapq.heappop(open_heap)
            state: State = (node_name, tick)

            if state in closed:
                continue
            closed.add(state)

            if node_name == goal.name:
                return came_from, state

            if tick >= deadline:
                continue

            node = self.graph.get_node(node_name)

            if self.reservations.is_node_free(node, tick + 1):
                wait_state: State = (node_name, tick + 1)
                wait_g = g + 1.0
                if wait_state not in closed and wait_g < g_score.get(
                    wait_state, float("inf")
                ):
                    g_score[wait_state] = wait_g
                    came_from[wait_state] = (state, "wait", None)
                    counter += 1
                    h = self._goal_dist.get(node_name, float("inf"))
                    heapq.heappush(
                        open_heap,
                        (wait_g + h, wait_g, counter, node_name, tick + 1),
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

                if not self.reservations.is_edge_free(edge, tick + 1, duration):
                    continue
                if not self.reservations.is_node_free(neighbor, arrival_tick):
                    continue

                move_state: State = (neighbor.name, arrival_tick)
                if move_state in closed:
                    continue

                move_g = g + duration
                if move_g < g_score.get(move_state, float("inf")):
                    g_score[move_state] = move_g
                    came_from[move_state] = (
                        state, "move", f"{node.name}_{neighbor.name}"
                    )
                    counter += 1
                    h = self._goal_dist.get(neighbor.name, float("inf"))
                    heapq.heappush(
                        open_heap,
                        (move_g + h, move_g, counter, neighbor.name, arrival_tick),
                    )

        return came_from, None

    def _commit_and_build(
        self,
        drone_id: int,
        came_from: CameFrom,
        goal_state: State,
        goal: Node,
    ) -> DronePlan:
        transitions: list[tuple[str, str | None, State, State]] = []
        state = goal_state
        while state in came_from:
            prev_state, action, edge_key = came_from[state]
            transitions.append((action, edge_key, prev_state, state))
            state = prev_state
        transitions.reverse()

        steps: list[PlannedStep] = []

        for action, edge_key, (from_name, from_tick), (to_name, to_tick) in (
            transitions
        ):
            to_node = self.graph.get_node(to_name)

            if action == "wait":
                self.reservations.reserve_node(to_node, to_tick)
                steps.append(
                    PlannedStep(tick=to_tick, node_name=to_name, connection_name=None)
                )
            else:
                from_node = self.graph.get_node(from_name)
                edge = from_node.get_edge_to(to_node)
                assert edge is not None
                duration = to_tick - from_tick

                self.reservations.reserve_edge(edge, from_tick + 1, duration)
                self.reservations.reserve_node(to_node, to_tick)

                for mid_tick in range(from_tick + 1, to_tick):
                    steps.append(
                        PlannedStep(
                            tick=mid_tick,
                            node_name=None,
                            connection_name=edge_key,
                        )
                    )
                steps.append(
                    PlannedStep(tick=to_tick, node_name=to_name, connection_name=None)
                )

        return DronePlan(drone_id=drone_id, end_node_name=goal.name, steps=steps)
