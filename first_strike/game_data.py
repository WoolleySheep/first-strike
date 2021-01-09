from dataclasses import dataclass, field
from typing import List, Tuple

Location = Tuple[float, float]


@dataclass
class Environment:
    width: float
    height: float
    timestep: float
    max_playtime: float


@dataclass
class RocketProperties:
    mass: float
    target_radius: float
    length: float
    main_engine_force: float
    thruster_force: float

    @property
    def moment_of_inertia(self) -> float:
        return (1 / 12) * self.mass * self.length ** 2


@dataclass
class TurretProperties:
    target_radius: float
    location: Location
    max_rotation_speed: float
    projectile_speed: float
    firing_interval: float


@dataclass
class Properties:
    rocket_properties: RocketProperties
    turret_properties: TurretProperties


@dataclass
class RocketHistory:
    locations: List[Location]
    angles: List[float]
    main_engine: List[float] = field(default_factory=lambda: [0.0])
    left_front_thruster: List[float] = field(default_factory=lambda: [0.0])
    left_rear_thruster: List[float] = field(default_factory=lambda: [0.0])
    right_front_thruster: List[float] = field(default_factory=lambda: [0.0])
    right_rear_thruster: List[float] = field(default_factory=lambda: [0.0])


@dataclass
class TurretHistory:
    angles: List[float]
    when_fired: List[float] = field(default_factory=list)


@dataclass
class ProjectileHistory:
    locations: List[Location]
    angle: float
    launch_time: float


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
