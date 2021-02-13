from dataclasses import dataclass
import math

from game_classes import Parameters, History, ObstacleParameters
from math_helpers import normalise_angle
from physics import Physics
from helpers import Helpers


@dataclass
class ControllerHelpers:
    parameters: Parameters
    history: History
    physics: Physics
    helpers: Helpers

    def calc_position_relative2rocket(self, location):

        return location - self.history.rocket.location

    def calc_angle2position_relative2rocket(self, location):

        return self.calc_position_relative2rocket(location).angle

    def calc_distance_between_rocket_and_position(self, location):

        return self.calc_position_relative2rocket(location).magnitude

    def calc_turret_position_relative2rocket(self):

        turret_location = self.parameters.turret.location

        return self.calc_position_relative2rocket(turret_location)

    def calc_dist_between_rocket_and_turret(self):

        turret_location = self.parameters.turret.location

        return self.calc_distance_between_rocket_and_position(turret_location)

    def calc_angle2turret_relative2rocket(self):

        turret_location = self.parameters.turret.location

        return self.calc_angle2position_relative2rocket(turret_location)

    def calc_projectile_location_relative2rocket(self, projectile):

        projectile_location = self.helpers.calc_projectile_location(projectile)

        return self.calc_position_relative2rocket(projectile_location)

    def calc_dist_between_rocket_and_projectile(self, projectile):

        return self.calc_projectile_location_relative2rocket(projectile).magnitude

    def calc_angle2projectile_relative2rocket(self, projectile):

        return self.calc_projectile_location_relative2rocket(projectile).angle

    def calc_obstacle_location_relative2rocket(self, obstacle: ObstacleParameters):

        return obstacle.location - self.history.rocket.location

    def calc_dist_between_rocket_and_obstacle(self, obstacle: ObstacleParameters):

        return self.calc_obstacle_location_relative2rocket(obstacle).magnitude

    def calc_angle_from_rocket2obstacle(self, obstacle: ObstacleParameters):

        return self.calc_obstacle_location_relative2rocket(obstacle).angle

    def firing_angle2hit_rocket(self):
        """https://math.stackexchange.com/questions/213545/solving-trigonometric-equations-of-the-form-a-sin-x-b-cos-x-c"""
        # TODO: Account for case where rocket is directly behind the turret and flying towards it
        #   - Existing method should be catching it, but the Divide by Zero isn't triggering because
        #     of floating point rubbish.  Consider switching to if's.

        projectile_speed = self.parameters.turret.projectile_speed
        turret_location = self.parameters.turret.location

        rocket_velocity = self.physics.calc_rocket_velocity()
        rocket_location = self.history.rocket.location

        try:
            k = (turret_location.y - rocket_location.y) / (
                turret_location.x - rocket_location.x
            )
        except ZeroDivisionError:  # k = inf
            try:
                m = math.asin(rocket_velocity.x / projectile_speed)
            except ValueError:  # Intercept is not possible due to rocket velocity
                return None

            beta = math.pi / 2
        else:
            try:
                a = -projectile_speed
                b = k * projectile_speed
                c = k * rocket_velocity.x - rocket_velocity.y
                m = math.asin(c / math.sqrt(a ** 2 + b ** 2))
            except ValueError:  # Intercept is not possible due to rocket velocity
                return None

            A = a / math.sqrt(a ** 2 + b ** 2)
            B = b / math.sqrt(a ** 2 + b ** 2)
            beta = math.atan2(B, A)

        firing_angle = normalise_angle(m - beta)
        if self.will_firing_angle_hit(firing_angle):
            return firing_angle
        return normalise_angle(math.pi - m - beta)

    def will_firing_angle_hit(self, theta):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        turret_location = self.parameters.turret.location
        projectile_speed = self.parameters.turret.projectile_speed

        try:
            x_intercept_time = (turret_location.x - rocket_location.x) / (
                rocket_velocity.x - projectile_speed * math.cos(theta)
            )
        except ZeroDivisionError:
            x_velocities_equal = True
            x_intercepts = math.isclose(turret_location.x, rocket_location.x)
        else:
            x_velocities_equal = False
            x_intercepts = x_intercept_time >= 0

        try:
            y_intercept_time = (turret_location.y - rocket_location.y) / (
                rocket_velocity.y - projectile_speed * math.sin(theta)
            )
        except ZeroDivisionError:
            y_velocities_equal = True
            y_intercepts = math.isclose(turret_location.y, rocket_location.y)
        else:
            y_velocities_equal = False
            y_intercepts = y_intercept_time >= 0

        return (
            not (x_velocities_equal and y_velocities_equal)
            and x_intercepts
            and y_intercepts
            and (
                math.isclose(x_intercept_time, y_intercept_time)
                or (x_velocities_equal is not y_velocities_equal)
            )
        )
