from pydantic import BaseModel

from .tick import TickResultDTO
from .graph import GraphDTO


class SimulationResponse(BaseModel):
    status_code: int = 200
    graph: GraphDTO
    history: list[TickResultDTO]
