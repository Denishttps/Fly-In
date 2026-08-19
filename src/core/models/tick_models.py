from dataclasses import dataclass, field


@dataclass(slots=True)
class DroneTickInfo:
    drone_id: int
    node_name: str | None
    connection_name: str | None = None
    is_finished: bool = False


@dataclass(slots=True)
class TickResult:
    tick: int
    is_finished: bool
    total_time: int
    drones: list[DroneTickInfo]


@dataclass
class PlannedStep:
    tick: int
    node_name: str | None
    connection_name: str | None


@dataclass
class DronePlan:
    drone_id: int
    end_node_name: str
    steps: list[PlannedStep] = field(default_factory=list)

    @property
    def makespan(self) -> int:
        return self.steps[-1].tick if self.steps else 0

    def info_at(self, tick: int) -> DroneTickInfo:
        if tick <= self.makespan and self.steps:
            step = self.steps[tick - 1]
            return DroneTickInfo(
                drone_id=self.drone_id,
                node_name=step.node_name,
                connection_name=step.connection_name,
                is_finished=(step.node_name == self.end_node_name),
            )
        return DroneTickInfo(
            drone_id=self.drone_id,
            node_name=self.end_node_name,
            connection_name=None,
            is_finished=True,
        )