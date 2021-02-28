from math_helpers import Coordinate, PolarCoordinate


class Helpers:
    def __init__(self, parameters, history):
        self.parameters = parameters
        self.history = history

    def is_rocket_within_bounds(self) -> bool:

        return self.is_within_bounds(self.history.rocket.location)

    def is_within_bounds(self, location: Coordinate) -> bool:

        w = self.parameters.environment.width
        h = self.parameters.environment.height

        return (-w / 2 <= location.x <= w / 2) and (-h / 2 <= location.y <= h / 2)

    def has_hit_obstacle(
        self, location: Coordinate, location_radius: float = 0.0
    ) -> bool:

        return any(
            location.distance2(obstacle.location) <= obstacle.radius + location_radius
            for obstacle in self.parameters.environment.obstacles
        )

    def has_rocket_hit_obstacle(self) -> bool:

        return self.has_hit_obstacle(
            self.history.rocket.location, self.parameters.rocket.target_radius
        )

    def can_turret_fire(self):

        last_fired = self.history.turret.last_fired

        if not last_fired:
            return True

        min_firing_interval = self.parameters.turret.min_firing_interval
        return self.history.time - last_fired >= min_firing_interval

    def does_rocket_impact_turret(self):

        rocket_radius = self.parameters.rocket.target_radius
        turret_radius = self.parameters.turret.radius
        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location

        return (
            rocket_location.distance2(turret_location) <= rocket_radius + turret_radius
        )

    def does_projectile_impact_rocket(self):

        target_radius = self.parameters.rocket.target_radius
        rocket_location = self.history.rocket.location

        return any(
            rocket_location.distance2(projectile_location) <= target_radius
            for projectile_location in self.get_active_projectile_locations()
        )

    def is_game_time_exceeded(self):

        current_time = self.history.time
        max_game_time = self.parameters.time.max_game_time
        timestep = self.parameters.time.timestep

        return current_time > max_game_time - timestep

    def calc_projectile_location(self, projectile):

        projectile_velocity = self.calc_projectile_velocity(projectile)
        dtime = self.history.time - projectile.launch_time

        return projectile_velocity * dtime + self.parameters.turret.location

    def calc_projectile_velocity(self, projectile):

        angle = projectile.firing_angle
        velocity = self.parameters.turret.projectile_speed

        return PolarCoordinate(velocity, angle).pol2cart()

    def get_active_projectile_locations(self):

        return [
            self.calc_projectile_location(projectile)
            for projectile in self.history.active_projectiles
        ]
