from core.drone_planner import DronePlanner
from core.search.astar import AStarSearch

from core.utils.load_map import load_map_from_file

from core.models.tick_models import TickResult, DroneTickInfo
from core.utils.init_drones import init_drones

from core.models.reservation import ReservationTable
from core.models.plan_models import DronePlan


class Dispatcher:
    def __init__(self, file_path: str) -> None:
        try:
            self.count, self.graph = load_map_from_file(file_path)
            self.drones = init_drones(self.count, self.graph)
        except FileNotFoundError:
            exit(1)
        finally:
            print("19 str dispatcher")

        self._history: list[TickResult] = []
        self._prev_positions: dict[int, str | None] = {}

        self.plans: dict[int, DronePlan] = {}

        self.plans = self._plan_time_expanded()
        self._history = self._build_history_from_plans()

    def _plan_time_expanded(self) -> dict[int, DronePlan]:
        reservations = ReservationTable()
        planner = DronePlanner(
            self.graph,
            reservations,
            search=AStarSearch(self.graph, reservations),
        )

        plans: dict[int, DronePlan] = {}
        for drone in sorted(self.drones, key=lambda d: d.id):
            plans[drone.id] = planner.plan(drone.id)

        return plans

    def _get_zero_tick(self, drone: DronePlan) -> DroneTickInfo:
        return DroneTickInfo(
            drone.drone_id,
            self.graph.start_node.name
        )

    def _build_history_from_plans(self) -> list[TickResult]:
        if not self.plans:
            return []

        first_infos = [
            self._get_zero_tick(self.plans[drone_id])
            for drone_id in sorted(self.plans)
        ]

        makespan = max(plan.makespan for plan in self.plans.values())
        total = len(self.plans)

        history: list[TickResult] = []
        history.append(
            TickResult(
                tick=0,
                is_finished=False,
                drones=first_infos
            )
        )
        for tick in range(1, makespan + 1):
            infos = [
                self.plans[drone_id].info_at(tick)
                for drone_id in sorted(self.plans)
            ]
            finished = sum(1 for info in infos if info.is_finished)
            history.append(
                TickResult(
                    tick=tick,
                    is_finished=(finished == total),
                    drones=infos,
                )
            )

        return history

    @property
    def total_turns(self) -> int:
        return self._history[-1].tick if self._history else 0

    @property
    def average_turns_per_drone(self) -> float:
        if not self.plans:
            return 0.0
        return sum(p.makespan for p in self.plans.values()) / len(self.plans)

    @staticmethod
    def _location_token(info: DroneTickInfo) -> str | None:
        if info.connection_name is not None:
            return info.connection_name
        return info.node_name

    def _format_tick_line(self, tick: TickResult) -> str | None:
        moves = []

        for info in tick.drones:
            token = self._location_token(info)
            if token is None:
                continue

            prev = self._prev_positions.get(info.drone_id)
            if token != prev:
                moves.append(f"D{info.drone_id}-{token}")

            self._prev_positions[info.drone_id] = token

        if not moves:
            return None

        return " ".join(moves)

    def compute_all(self) -> list[TickResult]:
        return self._history

    def print_simulation(self) -> list[TickResult]:
        self._prev_positions = {}

        for tick_result in self._history:
            line = self._format_tick_line(tick_result)
            if line is not None:
                print(line)

        return self._history
