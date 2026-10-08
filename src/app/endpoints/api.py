from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from ..services.simulation import SimulationService

from ..dependencies import get_simulation_service
from ..schemas.response import SimulationResponse

from ..schemas.file import FileDTO

from core.errors import MapNotFound, NoPlanFoundError, ParseError


router = APIRouter(
    prefix="/api/v1"
)

MAPS_ROOT = Path("maps").resolve()


def _resolve_map_path(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        candidate = p.resolve()
    elif p.parts and p.parts[0] == "maps":
        candidate = (Path.cwd() / p).resolve()
    else:
        candidate = (MAPS_ROOT / p).resolve()
    if candidate != MAPS_ROOT and MAPS_ROOT not in candidate.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access denied: '{path}' is outside maps/",
        )
    return str(candidate)


@router.get("/simulation", response_model=SimulationResponse)
def get_simulation(
    path: str,
    service: SimulationService = Depends(get_simulation_service)
) -> SimulationResponse:
    try:
        safe_path = _resolve_map_path(path)
        return service.get_simulation(safe_path)
    except HTTPException:
        raise
    except (ParseError, MapNotFound, FileNotFoundError,
            NoPlanFoundError, ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/getMaps")
def get_maps(
    service: SimulationService = Depends(get_simulation_service)
) -> list[FileDTO]:
    return service.get_all_maps()
