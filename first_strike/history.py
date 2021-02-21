from dataclasses import dataclass, field
from typing import List, Tuple

from math_helpers import Coordinate


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
    time: float = 0.0

    @property
    def active_projectiles(self):
        return [projectile for projectile in self.projectiles if projectile.on_board]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
