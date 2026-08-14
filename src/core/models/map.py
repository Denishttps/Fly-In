from dataclasses import dataclass, field


@dataclass
class RawHub:
    name: str
    x: int
    y: int
    metadata: dict[str, str | int] = field(default_factory=dict)
    is_start: bool = False
    is_end: bool = False


@dataclass
class RawConnection:
    source: str
    target: str
    max_capacity: int = 1


@dataclass
class MapData:
    drone_count: int
    hubs: list[RawHub] = field(default_factory=list)
    connections: list[RawConnection] = field(default_factory=list)
