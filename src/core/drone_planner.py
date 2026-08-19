from .models.graph import Graph
from .models.reservation import ReservationTable

from .models.plan_models import DronePlan
from .plan_builder import PlanBuilder

from .search.base import SpaceTimeSearch
from .time_errors import NoPlanFoundError


class DronePlanner:
    def __init__(
        self,
        graph: Graph,
        reservations: ReservationTable,
        search: SpaceTimeSearch,
        builder: PlanBuilder | None = None,
        default_horizon_padding: int = 40,
    ) -> None:
        self.graph = graph
        self.search_strategy = search
        self.builder = builder or PlanBuilder(graph, reservations)
        self._default_horizon_padding = default_horizon_padding

    def plan(
        self,
        drone_id: int,
        start_tick: int = 0,
        horizon_padding: int | None = None,
        max_horizon: int = 4000,
    ) -> DronePlan:
        start = self.graph.start_node
        goal = self.graph.end_node
        if start is None or goal is None:
            raise ValueError("Graph must have both a start zone and an end zone.")

        if start.name == goal.name:
            return DronePlan(drone_id=drone_id, end_node_name=goal.name)

        padding = (
            self._default_horizon_padding
            if horizon_padding is None
            else horizon_padding
        )

        h0 = self.search_strategy.cost_lower_bound(start.name)
        if h0 == float("inf"):
            raise NoPlanFoundError(
                f"No path exists from '{start.name}' to '{goal.name}'."
            )

        horizon = int(h0) + padding
        while horizon <= max_horizon:
            came_from, goal_state = self.search_strategy.search(
                start.name, goal.name, start_tick, horizon
            )
            if goal_state is not None:
                return self.builder.build(
                    drone_id, came_from, goal_state, goal.name
                )
            horizon *= 2

        raise NoPlanFoundError(
            f"Drone D{drone_id}: no conflict-free path to '{goal.name}' "
            f"found within {max_horizon} ticks — the network may be "
            "deadlocked by capacity constraints."
        )