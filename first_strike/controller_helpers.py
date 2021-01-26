from dataclasses import dataclass

from coordinate_classes import Coordinate, PolarCoordinate
from game_classes import Parameters, History, ProjectileHistory, ObstacleParameters
from math_helpers import calc_minimum_distance_between
from physics import Physics
from helpers import Helpers


@dataclass
class ControllerHelpers:
    parameters: Parameters
    history: History
    physics: Physics
    helpers: Helpers

    def calc_minimum_distance_between_rocket_and_projectile(
        self, projectile: ProjectileHistory
    ):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()
        projectile_location = self.helpers.calc_projectile_location(projectile)
        projectile_velocity = PolarCoordinate(
            self.parameters.turret.projectile_speed, projectile.firing_angle
        ).pol2cart()

        return calc_minimum_distance_between(
            rocket_location, rocket_velocity, projectile_location, projectile_velocity
        )

    def calc_minimum_distance_between_rocket_and_obstacle(
        self, obstacle: ObstacleParameters
    ):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        return calc_minimum_distance_between(
            rocket_location, rocket_velocity, obstacle.location, Coordinate(0.0, 0.0)
        )

    def calc_minimum_distance_between_rocket_and_turret(self):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()
        turret_location = self.parameters.turret.location

        return calc_minimum_distance_between(
            rocket_location, rocket_velocity, turret_location, Coordinate(0.0, 0.0)
        )

    def calc_turret_position_relative2rocket(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location

        return turret_location - rocket_location

    def calc_dist_from_rocket2turret(self):

        return self.calc_turret_position_relative2rocket().magnitude

    def calc_angle_from_rocket2turret(self):

        return self.calc_turret_position_relative2rocket().angle

    def calc_projectile_location_relative2rocket(self, projectile):

        rocket_location = self.history.rocket.location
        projectile_location = self.helpers.calc_projectile_location(projectile)

        return projectile_location - rocket_location

    def calc_dist_from_rocket2projectile(self, projectile):

        return self.calc_projectile_location_relative2rocket(projectile).magnitude

    def calc_angle_from_rocket2projectile(self, projectile):

        return self.calc_projectile_location_relative2rocket(projectile).angle

    def calc_obstacle_location_relative2rocket(self, obstacle: ObstacleParameters):

        return obstacle.location - self.history.rocket.location

    def calc_dist_from_rocket2obstacle(self, obstacle: ObstacleParameters):

        return self.calc_obstacle_location_relative2rocket(obstacle).magnitude

    def calc_angle_from_rocket2obstacle(self, obstacle: ObstacleParameters):

        return self.calc_obstacle_location_relative2rocket(obstacle).angle
