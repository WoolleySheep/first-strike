from coordinate_classes import Coordinate, PolarCoordinate
from game_helpers import get_engine_force, get_thruster_angle


def calc_rocket_velocity(self) -> Coordinate:

    locations = self.history.rocket.locations
    timestep = self.parameters.time.timestep

    if len(locations) < 2:
        return Coordinate(0.0, 0.0)

    return (locations[-1] - locations[-2]) / timestep


def calc_rocket_acceleration(self) -> Coordinate:

    locations = self.history.rocket.locations
    timestep = self.parameters.time.timestep

    if len(locations) < 3:
        return Coordinate(0.0, 0.0)

    v1 = (locations[-1] - locations[-2]) / timestep
    v2 = (locations[-2] - locations[-3]) / timestep

    return (v1 - v2) / timestep


def calc_rocket_angular_velocity(self) -> float:

    angles = self.history.rocket.angles
    timestep = self.parameters.time.timestep

    if len(angles) < 2:
        return 0.0

    return (angles[-1] - angles[-2]) / timestep


def calc_rocket_angular_acceleration(self) -> float:

    angles = self.history.rocket.angles
    timestep = self.parameters.time.timestep

    if len(angles) < 3:
        return 0.0

    theta1 = (angles[-1] - angles[-2]) / timestep
    theta2 = (angles[-2] - angles[-3]) / timestep

    return (theta1 - theta2) / timestep


def calc_main_engine_acceleration(self) -> Coordinate:

    angle = self.history.rocket.angles[-1]
    mass = self.parameters.rocket.mass
    force = self.parameters.rocket.max_main_engine_force

    f = PolarCoordinate(force, angle).pol2cart()

    return f / mass


def calc_thruster_acceleration(self, thruster: str) -> Coordinate:

    mass = self.parameters.rocket.mass

    force = get_engine_force(self, thruster)
    angle = get_thruster_angle(self, thruster)

    f = PolarCoordinate(force, angle).pol2cart()

    return f / mass


def calc_thruster_angular_acceleration(self, thruster: str) -> float:

    length = self.parameters.rocket.length
    moment_of_inertia = self.parameters.rocket.moment_of_inertia

    force = get_engine_force(self, thruster)

    mag_torque = force * length / 2
    mag_angular_acc = mag_torque / moment_of_inertia

    if thruster in ("left-front", "right-rear"):
        direction = -1
    elif thruster in ("right-front", "left-rear"):
        direction = 1
    else:
        raise ValueError(
            f"thruster must be one of {self.parameters.animation.thrusters}"
        )

    return direction * mag_angular_acc
