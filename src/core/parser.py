import re

from .errors import ParseError
from .models.map import RawConnection, RawHub, MapData


_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
_HUB_KEYS = ("start_hub", "end_hub", "hub")
_HUB_META_KEYS = ("color", "max_drones", "zone")
_CONN_META_KEYS = ("max_link_capacity",)
_ZONE_VALUES = ("normal", "priority", "restricted", "blocked")


class MapTextParser:
    @staticmethod
    def parse_text(text: str) -> MapData:
        drone_count = -1
        drone_line_no = 0
        hubs: list[RawHub] = []
        connections: list[RawConnection] = []
        hub_names: dict[str, int] = {}
        seen_connections: dict[frozenset[str], int] = {}
        start_count = 0
        end_count = 0

        raw_lines = text.splitlines()
        for idx, raw in enumerate(raw_lines, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones"):
                if drone_line_no != 0:
                    raise ParseError(
                        idx, "duplicate nb_drones definition"
                    )
                if ":" not in line:
                    raise ParseError(
                        idx,
                        "invalid nb_drones line, "
                        "expected 'nb_drones: <N>'",
                    )
                _, val = line.split(":", 1)
                val = val.strip()
                if not val:
                    raise ParseError(
                        idx,
                        "invalid nb_drones value, "
                        "expected a positive integer",
                    )
                try:
                    drone_count = int(val)
                except ValueError:
                    raise ParseError(
                        idx,
                        f"invalid nb_drones value '{val}', "
                        "expected a positive integer",
                    )
                if drone_count <= 0:
                    raise ParseError(
                        idx,
                        f"invalid nb_drones value '{val}', "
                        "expected a positive integer",
                    )
                drone_line_no = idx
            elif line.startswith("connection"):
                if ":" not in line:
                    raise ParseError(
                        idx,
                        "invalid connection line, "
                        "expected 'connection: <a>-<b>'",
                    )
                _, val = line.split(":", 1)
                connections.append(
                    MapTextParser._parse_connection(val.strip(), idx)
                )
                edge_key = frozenset(
                    {connections[-1].source, connections[-1].target}
                )
                if edge_key in seen_connections:
                    raise ParseError(idx, "duplicate connection")
                seen_connections[edge_key] = idx
            elif ":" in line:
                directive, val = line.split(":", 1)
                directive = directive.strip()
                if directive not in _HUB_KEYS:
                    raise ParseError(
                        idx, f"unknown directive '{directive}'"
                    )
                is_start = (directive == "start_hub")
                is_end = (directive == "end_hub")
                hub = MapTextParser._parse_hub(
                    val.strip(), is_start, is_end, idx
                )
                if hub.name in hub_names:
                    raise ParseError(
                        idx, f"duplicate zone '{hub.name}'"
                    )
                hub_names[hub.name] = idx
                hubs.append(hub)
                if is_start:
                    start_count += 1
                    if start_count > 1:
                        raise ParseError(idx, "multiple start zones defined")
                if is_end:
                    end_count += 1
                    if end_count > 1:
                        raise ParseError(idx, "multiple end zones defined")
            else:
                if line.startswith(("start_hub", "end_hub", "hub")):
                    raise ParseError(
                        idx, "invalid hub line, expected 'key: <name> <x> <y>'"
                    )
                raise ParseError(idx, f"unknown directive '{line}'")

        if drone_line_no == 0:
            raise ParseError(0, "missing nb_drones definition")
        if start_count == 0:
            raise ParseError(0, "missing start zone")
        if end_count == 0:
            raise ParseError(0, "missing end zone")

        for conn in connections:
            if conn.source not in hub_names:
                raise ParseError(
                    conn.line_no,
                    f"connection references undefined zone '{conn.source}'",
                )
            if conn.target not in hub_names:
                raise ParseError(
                    conn.line_no,
                    f"connection references undefined zone '{conn.target}'",
                )

        return MapData(
            drone_count=drone_count, hubs=hubs, connections=connections
        )

    @staticmethod
    def _parse_hub(
        hub_str: str, is_start: bool, is_end: bool, line_no: int
    ) -> RawHub:
        parts = hub_str.split(maxsplit=3)
        if len(parts) < 3:
            raise ParseError(
                line_no,
                "invalid hub line, "
                "expected '<name> <x> <y> [metadata]'",
            )
        if len(parts) > 4:
            raise ParseError(line_no, "invalid hub line, too many fields")
        name = parts[0]
        if not _NAME_RE.match(name):
            raise ParseError(
                line_no,
                f"invalid zone name '{name}', "
                "use only letters, digits and underscore",
            )
        try:
            x = int(parts[1])
        except ValueError:
            raise ParseError(
                line_no,
                f"invalid x coordinate '{parts[1]}', expected an integer",
            )
        try:
            y = int(parts[2])
        except ValueError:
            raise ParseError(
                line_no,
                f"invalid y coordinate '{parts[2]}', expected an integer",
            )
        metadata_str = parts[3] if len(parts) > 3 else ""
        metadata = MapTextParser._parse_hub_metadata(metadata_str, line_no)
        return RawHub(
            name=name, x=x, y=y,
            metadata=metadata,
            is_start=is_start,
            is_end=is_end
        )

    @staticmethod
    def _parse_connection(edge_str: str, line_no: int) -> RawConnection:
        if not edge_str:
            raise ParseError(
                line_no, "invalid connection line, expected '<a>-<b>'"
            )
        parts = edge_str.split(maxsplit=1)
        endpoints = parts[0]
        if endpoints.count("-") != 1:
            raise ParseError(
                line_no,
                f"invalid connection '{endpoints}', expected '<a>-<b>'",
            )
        source, target = endpoints.split("-")
        if not source or not target:
            raise ParseError(
                line_no,
                f"invalid connection '{endpoints}', expected '<a>-<b>'",
            )
        if not _NAME_RE.match(source):
            raise ParseError(
                line_no, f"invalid zone name '{source}' in connection"
            )
        if not _NAME_RE.match(target):
            raise ParseError(
                line_no, f"invalid zone name '{target}' in connection"
            )
        if source == target:
            raise ParseError(
                line_no,
                f"invalid self-connection '{source}-{target}'",
            )
        metadata_str = parts[1] if len(parts) > 1 else ""
        metadata = MapTextParser._parse_conn_metadata(metadata_str, line_no)
        max_capacity = metadata.get("max_link_capacity", 1)
        assert isinstance(max_capacity, int)
        return RawConnection(
            source=source, target=target,
            max_capacity=max_capacity, line_no=line_no,
        )

    @staticmethod
    def _parse_hub_metadata(
        metadata_str: str, line_no: int
    ) -> dict[str, str | int]:
        if not metadata_str:
            return {}
        if not (
            metadata_str.startswith("[") and metadata_str.endswith("]")
        ):
            raise ParseError(line_no, "invalid metadata, expected '[...]'")
        result: dict[str, str | int] = {}
        for item in metadata_str[1:-1].strip().split():
            if "=" not in item:
                raise ParseError(
                    line_no, f"invalid metadata entry '{item}'"
                )
            k, v = item.split("=", 1)
            if k not in _HUB_META_KEYS:
                raise ParseError(
                    line_no, f"unknown metadata key '{k}'"
                )
            if not v:
                raise ParseError(
                    line_no, f"invalid metadata value for '{k}'"
                )
            if k == "max_drones":
                try:
                    iv = int(v)
                except ValueError:
                    raise ParseError(
                        line_no,
                        f"invalid max_drones value '{v}', "
                        "expected a positive integer",
                    )
                if iv <= 0:
                    raise ParseError(
                        line_no,
                        f"invalid max_drones value '{v}', "
                        "expected a positive integer",
                    )
                result[k] = iv
            elif k == "zone":
                if v not in _ZONE_VALUES:
                    raise ParseError(
                        line_no,
                        f"invalid zone type '{v}', "
                        "expected one of: normal, priority, "
                        "restricted, blocked",
                    )
                result[k] = v
            else:
                result[k] = v
        return result

    @staticmethod
    def _parse_conn_metadata(
        metadata_str: str, line_no: int
    ) -> dict[str, int]:
        if not metadata_str:
            return {}
        if not (
            metadata_str.startswith("[") and metadata_str.endswith("]")
        ):
            raise ParseError(line_no, "invalid metadata, expected '[...]'")
        result: dict[str, int] = {}
        for item in metadata_str[1:-1].strip().split():
            if "=" not in item:
                raise ParseError(
                    line_no, f"invalid metadata entry '{item}'"
                )
            k, v = item.split("=", 1)
            if k not in _CONN_META_KEYS:
                raise ParseError(
                    line_no, f"unknown metadata key '{k}'"
                )
            if not v:
                raise ParseError(
                    line_no, f"invalid metadata value for '{k}'"
                )
            try:
                iv = int(v)
            except ValueError:
                raise ParseError(
                    line_no,
                    f"invalid max_link_capacity value '{v}', "
                    "expected a positive integer",
                )
            if iv <= 0:
                raise ParseError(
                    line_no,
                    f"invalid max_link_capacity value '{v}', "
                    "expected a positive integer",
                )
            result[k] = iv
        return result
