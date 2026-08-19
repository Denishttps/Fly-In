from dataclasses import dataclass


@dataclass(slots=True)
class DroneTickInfo:
    drone_id: int
    node_name: str
    is_finished: bool


@dataclass(slots=True)
class TickResult:
    tick: int
    is_finished: bool
    duty: int
    total_time: int
    drones: list[DroneTickInfo]
