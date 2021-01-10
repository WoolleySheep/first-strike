from dataclasses import dataclass, field
from typing import List


@dataclass
class Coordinate:
    x: float
    y: float

    def __add__(self, other):
        return self.x + other.x, self.y + other.y

@dataclass
class Environment:
    width: float
    height: float
    timestep: float
    max_game_time: float


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
    angle: float
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
