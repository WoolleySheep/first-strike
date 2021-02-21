import math
from typing import Tuple

from math_helpers import normalise_angle, Coordinate, PolarCoordinate


class Physics:
    def __init__(self, parameters, history):
        self.parameters = parameters
        self.history = history

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

    def get_engine_force_by_label(self, engine: str) -> float:

        labels = self.parameters.rocket.engine_labels
        forces = self.history.rocket.engine_forces

        for label, force in zip(labels, forces):
            if engine == label:
                return force

        raise ValueError(f"Engine must be in {labels}")

    #########################
    # TO BE CHANGED
    #########################

    def calc_main_engine_acceleration(self) -> Coordinate:

        angle = self.history.rocket.angle
        mass = self.parameters.rocket.mass
        force = self.parameters.rocket.max_main_engine_force

        f = PolarCoordinate(force, angle).pol2cart()

        return f / mass

    def calc_thruster_acceleration(self, thruster: str) -> Coordinate:

        mass = self.parameters.rocket.mass
        force = self.get_engine_force(thruster)
        angle = self.calc_thruster_angle(thruster)

        f = PolarCoordinate(force, angle).pol2cart()

        return f / mass

    def calc_thruster_torque(self, thruster: str) -> Coordinate:

        rocket = self.parameters.rocket
        length = self.parameters.rocket.length
        force = self.get_engine_force(thruster)
        direction = rocket.get_thruster_moment_direction(thruster)

        return direction * force * length / 2

    def calc_thruster_angular_acceleration(self, thruster: str) -> float:

        torque = self.calc_thruster_torque(thruster)
        moment_of_inertia = self.parameters.rocket.moment_of_inertia

        return torque / moment_of_inertia

    def calc_thruster_angle(self, thruster):

        rocket = self.parameters.rocket
        thruster_direction = rocket.get_thruster_force_direction(thruster)
        rocket_angle = self.history.rocket.angle

        return normalise_angle(rocket_angle - thruster_direction * math.pi / 2)
