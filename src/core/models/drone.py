from pydantic import BaseModel, Field
from core.models.node import Node


class Drone(BaseModel):
    id: int = Field(..., description="Unique identifier for the drone")
    x: float = Field(..., description="X-coordinate of the drone's position")
    y: float = Field(..., description="Y-coordinate of the drone's position")
    
    hub: Node | None = Field(None, description="The hub node where the drone is currently located")