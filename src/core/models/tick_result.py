from dataclasses import dataclass


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