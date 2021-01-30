from dataclasses import dataclass, field
from typing import List

from coordinate_classes import Coordinate


@dataclass
class AnimationParameters:
    fps: float
    square_root_board_area_barrel_length_ratio: float
    rocket_length_engine_bridge_width_ratio: float
    rocket_length_max_thrust_length_ratio: float
    thrust_cone_angle: float
    game_over_alpha: float
    default_title: str
    engine_labels: List[str]

    @property
    def frame_interval_ms(self) -> int:
        """Frame interval in ms"""
        return int(1000 / self.fps)

    @property
    def thruster_labels(self) -> List[str]:
        return self.engine_labels[1:]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


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

    @property
    def board_area(self) -> float:
        return self.width * self.height

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
    target_radius: float
    length: float
    max_main_engine_force: float
    max_thruster_force: float

    @property
    def moment_of_inertia(self) -> float:
        return (1 / 12) * self.mass * self.length ** 2

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class TurretParameters:
    target_radius: float
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
    animation: AnimationParameters
    environment: EnvironmentParameters
    time: TimeParameters
    rocket: RocketParameters
    turret: TurretParameters

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class RocketHistory:
    locations: List[Coordinate]
    angles: List[float]
    main_engine_forces: List[float] = field(default_factory=list)
    left_front_thruster_forces: List[float] = field(default_factory=list)
    left_rear_thruster_forces: List[float] = field(default_factory=list)
    right_front_thruster_forces: List[float] = field(default_factory=list)
    right_rear_thruster_forces: List[float] = field(default_factory=list)

    @property
    def location(self) -> Coordinate:
        return self.locations[-1]

    @property
    def angle(self) -> float:
        return self.angles[-1]

    @property
    def main_engine_force(self) -> float:
        return self.main_engine_forces[-1]

    @property
    def left_front_thruster_force(self) -> float:
        return self.left_front_thruster_forces[-1]

    @property
    def left_rear_thruster_force(self) -> float:
        return self.left_rear_thruster_forces[-1]

    @property
    def right_front_thruster_force(self) -> float:
        return self.right_front_thruster_forces[-1]

    @property
    def right_rear_thruster_force(self) -> float:
        return self.right_rear_thruster_forces[-1]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class TurretHistory:
    angles: List[float]
    rotation_velocities: List[float] = field(default_factory=list)
    when_fired: List[float] = field(default_factory=list)

    @property
    def angle(self) -> float:
        return self.angles[-1]

    @property
    def rotation_velocity(self) -> float:
        return self.rotation_velocities[-1]

    @property
    def last_fired(self) -> float:

        try:
            return self.when_fired[-1]
        except IndexError:
            return

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class ProjectileHistory:
    firing_angle: float
    launch_time: float
    on_board: bool

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class History:
    rocket: RocketHistory
    turret: TurretHistory
    projectiles: List[ProjectileHistory] = field(default_factory=list)
    timesteps: List[float] = field(default_factory=lambda: [0.0])

    @property
    def time(self) -> float:
        return self.timesteps[-1]

    @property
    def active_projectiles(self):
        return [projectile for projectile in self.projectiles if projectile.on_board]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
