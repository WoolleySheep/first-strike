from dataclasses import dataclass, field
import math
from typing import List


@dataclass
class Coordinate:
    x: float
    y: float

    def __add__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x + other.x, self.y + other.y)
        return Coordinate(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x - other.x, self.y - other.y)
        return Coordinate(self.x - other, self.y - other)

    def __mul__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x * other.x, self.y * other.y)
        return Coordinate(other * self.x, other * self.y)

    def __truediv__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x / other.x, self.y / other.y)
        return Coordinate(self.x / other, self.y / other)

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __dtruediv__(self, other):
        return self.__truediv__(other)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Only two elements in class")

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    def cart2pol(self):
        r = self.magnitude()
        theta = self.angle()

        return PolarCoordinate(r, theta)


@dataclass
class PolarCoordinate:
    r: float
    theta: float

    def pol2cart(self):
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)

        return Coordinate(x, y)


@dataclass
class Environment:
    width: float
    height: float
    timestep: float
    max_game_time: float

    @property
    def board_area(self) -> float:
        return self.width * self.height


@dataclass
class RocketProperties:
    mass: float
    target_radius: float
    length: float
    max_main_engine_force: float
    max_thruster_force: float

    @property
    def moment_of_inertia(self) -> float:
        return (1 / 12) * self.mass * self.length ** 2


@dataclass
class TurretProperties:
    target_radius: float
    location: Coordinate
    max_rotation_speed: float
    projectile_speed: float
    min_firing_interval: float


@dataclass
class Properties:
    rocket_properties: RocketProperties
    turret_properties: TurretProperties


@dataclass
class RocketHistory:
    locations: List[Coordinate]
    angles: List[float]
    main_engine_forces: List[float] = field(default_factory=list)
    left_front_thruster_forces: List[float] = field(default_factory=list)
    left_rear_thruster_forces: List[float] = field(default_factory=list)
    right_front_thruster_forces: List[float] = field(default_factory=list)
    right_rear_thruster_forces: List[float] = field(default_factory=list)


@dataclass
class TurretHistory:
    angles: List[float]
    rotation_velocities: List[float] = field(default_factory=list)
    when_fired: List[float] = field(default_factory=list)


@dataclass
class ProjectileHistory:
    locations: List[Coordinate]
    firing_angle: float
    launch_time: float
    on_board: bool


@dataclass
class History:
    rocket_history: RocketHistory
    turret_history: TurretHistory
    projectile_histories: List[ProjectileHistory] = field(default_factory=list)
    timesteps: List[float] = field(default_factory=lambda: [0.0])


@dataclass
class GameData:
    environment: Environment
    properties: Properties
    history: History
