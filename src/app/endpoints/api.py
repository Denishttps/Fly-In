from fastapi import APIRouter, Depends, HTTPException, status
from ..services.simulation import SimulationService

from ..dependencies import get_simulation_service
from ..schemas.response import SimulationResponse

from ..schemas.file import FileDTO


router = APIRouter(
    prefix="/api/v1"
)


@router.get("/simulation", response_model=SimulationResponse)
def get_simulation(
    path: str,
    service: SimulationService = Depends(get_simulation_service)
) -> SimulationResponse:
    try:
        return service.get_simulation(path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Map not found"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error"
        )


@router.get("/getMaps")
def get_maps(
    service: SimulationService = Depends(get_simulation_service)
) -> list[FileDTO]:
    return service.get_all_maps()
