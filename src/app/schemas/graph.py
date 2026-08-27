from pydantic import BaseModel, ConfigDict
from core.models.zone_type import ZoneType


class NodeMetaDataDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    color: str | None = None
    max_drones: int = 1
    zone: ZoneType = ZoneType.NORMAL


class NodeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    x: int
    y: int
    metadata: NodeMetaDataDTO


class EdgeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: NodeDTO
    target: NodeDTO
    max_capacity: int = 1


class GraphDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    edges: list[EdgeDTO]
    nodes: list[NodeDTO]
