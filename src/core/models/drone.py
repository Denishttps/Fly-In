from dataclasses import dataclass


@dataclass
class Drone:
    id: int
    color: str | None = None
