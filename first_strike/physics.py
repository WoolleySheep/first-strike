from coordinate_classes import Coordinate, PolarCoordinate


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

        length = self.parameters.rocket.length
        force = self.get_engine_force(thruster)
        direction = self.get_thruster_rotation_direction(thruster)

        return direction * force * length / 2

    def calc_thruster_angular_acceleration(self, thruster: str) -> float:

        torque = self.calc_thruster_acceleration(thruster)
        moment_of_inertia = self.parameters.rocket.moment_of_inertia

        return torque / moment_of_inertia

    def calc_thruster_angle(self, thruster):

        angle = self.history.rocket.angle
        direction = self.get_thruster_direction(thruster)

        return normalise_angle(angle - direction * math.pi / 2)

    def get_engine_force(self, engine):

        if engine == "main":
            return self.history.rocket.main_engine_force
        if engine == "left-front":
            return self.history.rocket.left_front_thruster_force
        if engine == "left-rear":
            return self.history.rocket.left_rear_thruster_force
        if engine == "right-front":
            return self.history.rocket.right_front_thruster_force
        if engine == "right-rear":
            return self.history.rocket.right_rear_thruster_force

        raise ValueError(f"Engine must be in {self.parameters.animation.engine_labels}")

    def get_thruster_direction(self, thruster):

        if thruster in ("left-front", "left-rear"):
            return 1
        if thruster in ("right-front", "right-rear"):
            return -1

        raise ValueError(
            f"Thruster must be one of {self.parameters.animation.thruster_labels}"
        )

    def get_thruster_rotation_direction(self, thruster):

        if thruster in ("left-front", "right-rear"):
            return -1
        elif thruster in ("right-front", "left-rear"):
            return 1
        else:
            raise ValueError(
                f"Thruster must be one of {self.parameters.animation.thruster_labels}"
            )
