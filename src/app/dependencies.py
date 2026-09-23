from .services.simulation import SimulationService


def get_simulation_service() -> SimulationService:
    return SimulationService()
