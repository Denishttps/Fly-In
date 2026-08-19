from dataclasses import dataclass

@dataclass(slots=True)
class TickResult:
    tick: int
    is_finished: bool
    duty: int
    total_time: int
    drone_statuses: list[str]
