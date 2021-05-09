"""Defines the parameters class and all composition classes."""

from dataclasses import dataclass
from typing import List, Tuple

from math_helpers import Coordinate


@dataclass
class ObstacleParameters:
    """An obstacle on the board.

    If a rocket collides with an obstacle, the rocket will lose.
    If a projectile collides with an obstacle, the projectile will be destroyed.

    Attributes
    ----------
    location (m): The location of the obstacle as an (x, y) coordinate
    radius (m): The radius of the obstacle.

    Methods
    ----------
    has_hit: Has an object hit the obstacle.
    """

    location: Coordinate
    radius: float

    def has_hit(self, coord: Coordinate) -> bool:
        """Has an object hit the obstacle."""
        return self.location.distance2(coord) <= self.radius

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class EnvironmentParameters:
    """Parameters defining the game board.

    Attributes
    ----------
    Width (m): Width of the game board.
    Height (m): Height of the game board.
    Obstacles: All of the obstacles on the board.
    """

    width: float
    height: float
    obstacles: List[ObstacleParameters]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class TimeParameters:
    """Parmeters defining time within the game.

    Attributes
    ----------
    timestep (s): Duration of the timestep between each game turn.
    max_game_time (s): If game time exceeds this value, it will be declared a draw.
    """

    timestep: float
    max_game_time: float

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class RocketParameters:
    """Parameters defining the rocket.

    The rocket consists of 5 engines, including 1 main engine and 4 thrusters.
    The main engine is positioned at the tail of the rocket in line with the main axis.
    The thrusters are positioned at the nose/tail of the rocket, perpendicular to the main axis.

    Attributes
    ----------
    mass (kg): Mass of the rocket
    length (m): Length of the rocket (nose-to-tail)
    max_main_engine_force (N): Maximum thrust the main engine can generate.
    max_thruster_force: Maximum thrust each of the thrusters can generate.
    engine_labels: Names of each of the engines.
    target_radius (m): Effective radius of the rocket for determining collisions.
    moment_of_inertia (kg*m^2): Moment of inertia of the rocket around the center of mass.
    abs_thruster_moment_arm (N*m): Absolute moment arm of all thrusters.
    thruster_labels: The names of each of the thrusters.

    Methods
    ----------
    get_thruster_force_direction: Calculate the sign of the force generated by a thruster relative to the rocket axis.
    get_thruster_moment_direction: Calculate the sign of the moment generated by a thruster on the rocket center of mass.
    calc_thruster_torque: Calculate the torque generated by a thruster on the rocket center of mass.
    calc_thruster_angular_acc: Calculate the angular acceleration generated by a thruster on the rocket's center of mass.
    calc_angular_acc: Calculate the total angular acceleration generated by the thrusters on the rocket center of mass.
    """

    mass: float
    length: float
    max_main_engine_force: float
    max_thruster_force: float
    engine_labels: Tuple[str, str, str, str, str] = (
        "main",
        "left-front",
        "left-rear",
        "right-front",
        "right-rear",
    )

    @property
    def target_radius(self) -> float:
        """(m) Effective radius of the rocket for determining collisions."""
        return self.length / 2

    @property
    def moment_of_inertia(self) -> float:
        """(kg*m^2) Moment of inertia of the rocket around the center of mass.

        Rocket can be treated as a beam with zero width and evenly distributed mass.
        https://en.wikipedia.org/wiki/List_of_moments_of_inertia
        """
        return (1 / 12) * self.mass * self.length ** 2

    @property
    def abs_thruster_moment_arm(self) -> float:
        """(Nm) Absolute moment arm of all thrusters.

        All thrusters are located at the very nose/tail of the rocket.
        All thrusters are exactly perpendicular the the rocket axis.

        """
        return self.length / 2

    @property
    def thruster_labels(self) -> Tuple[str, str, str, str]:
        return self.engine_labels[1:]

    def get_thruster_force_direction(self, thruster: str) -> int:
        """Calculate the sign of the force generated by a thruster relative to the rocket axis.

        Direction is determined as if there was a cartesian coordinate system
        attached to the rocket, with the rocket axis lying on the y axis.
        - Thrusters pushing the rocket right are positive.
        - Thrusters pushing the rocket left are negative.

        Arguments
        ----------
        thruster: Name of the thruster.

        Return
        ----------
        direction: Direction of the thruster force.
        """

        if thruster in ("left-front", "left-rear"):
            return 1
        if thruster in ("right-front", "right-rear"):
            return -1

        raise ValueError(f"Thruster must be one of {self.thruster_labels}")

    def get_thruster_moment_direction(self, thruster: str) -> int:
        """Calculate the sign of the moment generated by a thruster on the rocket center of mass.

        - Thrusters pushing the rocket clockwise are negative.
        - Thrusters pushing the rocket counter-clockwise are positive.

        Arguments
        ----------
        thruster: Name of the thruster.

        Return
        ----------
        rotation_direction: Rotation direction generated.
        """

        if thruster in ("left-front", "right-rear"):
            return -1
        elif thruster in ("right-front", "left-rear"):
            return 1
        else:
            raise ValueError(f"Thruster must be one of {self.thruster_labels}")

    def calc_thruster_torque(self, thruster: str, force: float) -> float:
        """Calculate the torque generated by a thruster on the rocket center of mass.

        Arguments
        ----------
        thruster: Name of the thruster.
        force (N): Thrust generated by the engine.

        Return
        ----------
        torque (Nm): Torque generated.
        """

        moment_direction = self.get_thruster_moment_direction(thruster)

        return force * moment_direction * self.abs_thruster_moment_arm

    def calc_thruster_angular_acc(self, thruster: str, force) -> float:
        """Calculate the angular acceleration generated by a thruster on the rocket center of mass.

        Arguments
        ----------
        thruster: Name of the thruster.
        force (N): Thrust generated by the engine.

        Return
        ----------
        angular_acceleration (N/m^2): Angular acceleration generated.
        """

        torque = self.calc_thruster_torque(thruster, force)

        return torque / self.moment_of_inertia

    def calc_angular_acc(
        self, thruster_forces: Tuple[float, float, float, float]
    ) -> float:
        """Calculate the total angular acceleration generated by the thrusters on the rocket center of mass.

        Arguments
        ----------
        thruster_forces (N): Force of each of the thrusters in the same order they are stored in thruster_labels.

        Return
        ----------
        angular_acceleration (N/m^2): Angular acceleration of the rocket.
        """

        return sum(
            self.calc_thruster_angular_acc(t, f)
            for t, f in zip(self.thruster_labels, thruster_forces)
        )

    def calc_abs_acc(self, force: float) -> float:
        """Calculate the magnitude of the acceleration generated by a force on the rocket.

        Arguments
        ----------
        force (N): Force on the rocket.

        Return
        ----------
        mag_acc (m/s^2): Magnitude of acceleration generated.
        """

        return force / self.mass

    def calc_acc_relative2rocket(
        self, engine_forces: Tuple[float, float, float, float, float]
    ) -> Coordinate:
        """Calculate the total acceleration generated by the engines on the rocket relative to the rocket orientation.

        Current rocket axis is treated as the y axis for this coordinate system.

        Arguments
        ----------
        engine_forces (N): Force of each of the engines in the same order they are stored in engine_labels.

        Return
        ----------
        relative_acc (m/s^2): Acceleration of the rocket relative to the rocket orientation.
        """

        thruster_forces = engine_forces[1:]

        horizontal_acc = sum(
            self.get_thruster_force_direction(t) * self.calc_abs_acc(f)
            for t, f in zip(self.thruster_labels, thruster_forces)
        )
        vertical_acc = self.calc_abs_acc(engine_forces[0])

        return Coordinate(horizontal_acc, vertical_acc)

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
