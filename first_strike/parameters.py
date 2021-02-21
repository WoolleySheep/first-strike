from dataclasses import dataclass
from typing import List, Tuple

from math_helpers import Coordinate


@dataclass
class ObstacleParameters:
    location: Coordinate
    radius: float

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class EnvironmentParameters:
    width: float
    height: float
    obstacles: List[ObstacleParameters]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class TimeParameters:
    timestep: float
    max_game_time: float

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class RocketParameters:
    mass: float
    length: float
    max_main_engine_force: float
    max_thruster_force: float
    engine_labels: Tuple[str] = (
        "main",
        "left-front",
        "left-rear",
        "right-front",
        "right-rear",
    )

    @property
    def target_radius(self) -> float:
        return self.length / 2

    @property
    def moment_of_inertia(self) -> float:
        return (1 / 12) * self.mass * self.length ** 2

    @property
    def thruster_labels(self) -> Tuple[str]:
        return self.engine_labels[1:]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class TurretParameters:
    radius: float
    location: Coordinate
    max_rotation_speed: float
    projectile_speed: float
    min_firing_interval: float

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class Parameters:
    environment: EnvironmentParameters
    time: TimeParameters
    rocket: RocketParameters
    turret: TurretParameters

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
