import math

from controller import Controller
from coordinate_classes import Coordinate, PolarCoordinate
from math_helpers import normalise_angle, calc_minimum_distance_between


class TurretController(Controller):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(parameters, history, physics, helpers)

    def calc_inputs(self):

        if not self.helpers.can_turret_fire():
            return self.calc_rotation_velocity(), False

        # TODO: Allow turret to fire if it will hit the rocket before the obstacle
        if (
            self.will_projectile_hit_rocket_within_bounds()
            and self.will_projectile_hit_rocket_before_obstacle()
        ):
            return self.calc_rotation_velocity(), True

        return self.calc_rotation_velocity(), False

    def calc_rotation_velocity(self):

        delta_angle = normalise_angle(
            self.calc_intercept_angle() - self.history.turret.angle
        )
        mag_rotation_speed = min(
            self.parameters.turret.max_rotation_speed,
            abs(delta_angle) / self.parameters.time.timestep,
        )  # Take a smaller step if a full move would carry past the rocket

        return (1 if delta_angle >= 0 else -1) * mag_rotation_speed

    def calc_intercept_angle(self):
        """https://math.stackexchange.com/questions/213545/solving-trigonometric-equations-of-the-form-a-sin-x-b-cos-x-c"""
        # TODO: Account for case where rocket is directly behind the turret and flying towards it
        #   - Existing method should be catching it, but the Divide by Zero isn't triggering because
        #     of floating point rubbish.  Consider switching to if's.

        def valid_angle(theta):

            try:
                xt = (turret_location.x - rocket_location.x) / (
                    rocket_velocity.x - projectile_speed * math.cos(theta)
                )
                x_equal = False
                x_intercepts = xt >= 0
            except ZeroDivisionError:  # x velocity of rocket and projectile are the same
                x_equal = True
                x_intercepts = math.isclose(turret_location.x, rocket_location.x)

            try:
                yt = (turret_location.y - rocket_location.y) / (
                    rocket_velocity.y - projectile_speed * math.sin(theta)
                )
                y_equal = False
                y_intercepts = yt >= 0
            except ZeroDivisionError:  # y velocity of rocket and projectile are the same
                y_equal = True
                y_intercepts = math.isclose(turret_location.y, rocket_location.y)

            return (
                not (x_equal and y_equal)
                and x_intercepts
                and y_intercepts
                and ((x_equal is not y_equal) or math.isclose(xt, yt))
            )

        projectile_speed = self.parameters.turret.projectile_speed
        turret_location = self.parameters.turret.location

        rocket_velocity = self.physics.calc_rocket_velocity()
        rocket_location = self.history.rocket.location

        try:
            try:
                k = (turret_location.y - rocket_location.y) / (
                    turret_location.x - rocket_location.x
                )

                a = -projectile_speed
                b = k * projectile_speed
                c = k * rocket_velocity.x - rocket_velocity.y

                A = a / math.sqrt(a ** 2 + b ** 2)
                B = b / math.sqrt(a ** 2 + b ** 2)
                beta = math.atan2(B, A)

                m = math.asin(c / math.sqrt(a ** 2 + b ** 2))

            except ZeroDivisionError:  # k = inf
                beta = math.pi / 2
                m = math.asin(rocket_velocity.x / projectile_speed)

        except ValueError:  # Intercept is no longer possible due to rocket velocity
            return self.calc_angle2rocket()  # Track the rocket

        intercept_angle = normalise_angle(m - beta)
        if valid_angle(intercept_angle):
            return intercept_angle
        return normalise_angle(math.pi - m - beta)

    def will_projectile_hit_rocket_within_bounds(self):

        safety_buffer = 2.0

        projectile_location = self.parameters.turret.location
        projectile_speed = self.parameters.turret.projectile_speed
        projectile_angle = self.history.turret.angle
        projectile_velocity = PolarCoordinate(
            projectile_speed, projectile_angle
        ).pol2cart()

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        (
            _,
            dist_closest,
            (rocket_closest_loc, projectile_closest_loc),
        ) = calc_minimum_distance_between(
            rocket_location, rocket_velocity, projectile_location, projectile_velocity
        )

        return (
            dist_closest <= self.parameters.rocket.target_radius / 2
            and self.helpers.is_within_bounds(rocket_closest_loc)
            and self.helpers.is_within_bounds(projectile_closest_loc)
        )

    def will_projectile_hit_rocket_before_obstacle(self):

        projectile_location = self.parameters.turret.location
        projectile_speed = self.parameters.turret.projectile_speed
        projectile_angle = self.history.turret.angle
        projectile_velocity = PolarCoordinate(
            projectile_speed, projectile_angle
        ).pol2cart()

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        t_rocket, _, _ = calc_minimum_distance_between(
            projectile_location, projectile_velocity, rocket_location, rocket_velocity
        )

        for obstacle in self.parameters.environment.obstacles:
            (
                t_obstacle,
                dist_obstacle,
                (projectile_loc, _),
            ) = calc_minimum_distance_between(
                projectile_location,
                projectile_velocity,
                obstacle.location,
                Coordinate(0.0, 0.0),
            )
            if (
                dist_obstacle <= obstacle.radius
                and t_obstacle < t_rocket
                and self.helpers.is_within_bounds(projectile_loc)
            ):
                return False

        return True

    def calc_angle2rocket(self):

        return math.atan2(
            *(
                list(self.history.rocket.location - self.parameters.turret.location)[
                    ::-1
                ]
            )
        )
