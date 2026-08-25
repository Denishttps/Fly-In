from .models.graph import Graph
from .models.reservation import ReservationTable

from .models.plan_models import DronePlan, PlannedStep
from .search.base import CameFrom, State


class PlanBuilder:
    def __init__(self, graph: Graph, reservations: ReservationTable) -> None:
        self.graph = graph
        self.reservations = reservations

    def build(
        self,
        drone_id: int,
        came_from: CameFrom,
        goal_state: State,
        goal_name: str,
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
                    PlannedStep(
                        tick=to_tick, node_name=to_name, connection_name=None
                    )
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
                    PlannedStep(
                        tick=to_tick, node_name=to_name, connection_name=None
                    )
                )

        return DronePlan(
            drone_id=drone_id, end_node_name=goal_name, steps=steps
        )
