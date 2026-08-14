from .models.map import RawConnection, RawHub, MapData


class MapTextParser:
    @staticmethod
    def parse_text(text: str) -> MapData:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        drone_count = -1
        hubs: list[RawHub] = []
        connections: list[RawConnection] = []

        for line in lines:
            if line.startswith("nb_drones"):
                drone_count = int(line.split(":")[1].strip())
            elif line.startswith("connection"):
                _, val = line.split(":", 1)
                connections.append(
                    MapTextParser._parse_connection(val.strip())
                )
            elif ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                if key in ("start_hub", "end_hub", "hub"):
                    is_start = (key == "start_hub")
                    is_end = (key == "end_hub")
                    hubs.append(
                        MapTextParser._parse_hub(val.strip(), is_start, is_end)
                    )

        return MapData(
            drone_count=drone_count, hubs=hubs, connections=connections
        )

    @staticmethod
    def _parse_hub(hub_str: str, is_start: bool, is_end: bool) -> RawHub:
        parts = hub_str.split(maxsplit=3)
        name, x, y = parts[0], int(parts[1]), int(parts[2])
        metadata_str = parts[3] if len(parts) > 3 else ""
        metadata = MapTextParser._parse_metadata(metadata_str)
        return RawHub(
            name=name, x=x, y=y,
            metadata=metadata,
            is_start=is_start,
            is_end=is_end
        )

    @staticmethod
    def _parse_connection(edge_str: str) -> RawConnection:
        parts = edge_str.split(maxsplit=1)
        source, target = parts[0].split("-")
        metadata_str = parts[1] if len(parts) > 1 else ""
        metadata = MapTextParser._parse_metadata(metadata_str)
        max_capacity = int(metadata.get("max_link_capacity", 1))
        return RawConnection(
            source=source, target=target, max_capacity=max_capacity
        )

    @staticmethod
    def _parse_metadata(metadata_str: str) -> dict[str, str | int]:
        if not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            return {}
        result = {}
        for item in metadata_str[1:-1].strip().split():
            if "=" in item:
                k, v = item.split("=", 1)
                result[k] = int(v) if v.isdigit() else v
        return result
