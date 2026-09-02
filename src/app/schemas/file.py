from pydantic import BaseModel
from pathlib import Path


class FileDTO(BaseModel):
    name: str
    group: str
    path: Path
