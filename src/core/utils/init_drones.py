from ..models.drone import Drone


class DroneFactory:
    @staticmethod
    def create(count: int) -> list[Drone]:
        drones = []
        for i in range(count):
            drone = Drone(i + 1)
            drones.append(drone)
        return drones
