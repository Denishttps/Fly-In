from pydantic import BaseModel, ConfigDict


class DroneTickInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    drone_id: int
    node_name: str | None
    connection_name: str | None = None
    is_finished: bool = False


class TickResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tick: int
    is_finished: bool
    drones: list[DroneTickInfoDTO]
