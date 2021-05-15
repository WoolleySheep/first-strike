import math

from controller import Controller
from math_helpers import PolarCoordinate, RelativeObjects, normalise_angle


class TurretController(Controller):

    def calc_inputs(self):

        if not self.helpers.can_turret_fire():
            return self.calc_rotation_velocity(), False

        if (
            self.will_projectile_hit_rocket_within_bounds()
            and self.will_projectile_hit_rocket_before_obstacle()
        ):
            return self.calc_rotation_velocity(), True

        return self.calc_rotation_velocity(), False

    def calc_rotation_velocity(self):

        firing_angle = self.controller_helpers.firing_angle2hit_rocket()
        angle2rocket = self.calc_angle2rocket()
        if firing_angle is None or abs(firing_angle - angle2rocket) > math.pi / 2:
            firing_angle = (
                angle2rocket  # If firing angle is at > 90 deg, aim for the rocket
            )

        delta_angle = normalise_angle(firing_angle - self.history.turret.angle)
        abs_rotation_speed = min(
            self.parameters.turret.max_rotation_speed,
            abs(delta_angle) / self.parameters.time.timestep,
        )  # Take a smaller step if a full move would carry past the rocket

        return (1 if delta_angle >= 0 else -1) * abs_rotation_speed

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

        projectile2rocket = RelativeObjects(
            projectile_location, rocket_location, projectile_velocity, rocket_velocity
        )

        (
            min_dist,
            _,
            (projectile_location_min_dist, rocket_location_min_dist),
        ) = projectile2rocket.minimum_distance_between_objects()

        return (
            min_dist <= self.parameters.rocket.target_radius / safety_buffer
            and self.helpers.is_within_bounds(projectile_location_min_dist)
            and self.helpers.is_within_bounds(rocket_location_min_dist)
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

        projectile2rocket = RelativeObjects(
            projectile_location, rocket_location, projectile_velocity, rocket_velocity
        )

        rocket_output = projectile2rocket.time_objects_first_within_distance(
            self.parameters.rocket.target_radius
        )
        if rocket_output is None:
            return False  # Doesn't hit rocket at all
        time_rocket_intercept, _ = rocket_output

        for obstacle in self.parameters.environment.obstacles:
            projectile2obstacle = RelativeObjects(
                projectile_location, obstacle.location, projectile_velocity
            )
            obstacle_output = projectile2obstacle.time_objects_first_within_distance(
                obstacle.radius
            )
            if obstacle_output is None:
                continue
            time_obstacle_intercept, _ = obstacle_output
            if time_obstacle_intercept < time_rocket_intercept:
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
