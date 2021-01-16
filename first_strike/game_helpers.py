import math

from coordinate_classes import Coordinate
from math_helpers import normalise_angle, distance_between_coordinates


def is_within_bounds(self, location: Coordinate) -> bool:

    w = self.parameters.environment.width
    h = self.parameters.environment.height

    return (-w / 2 <= location.x <= w / 2) and (-h / 2 <= location.y <= h / 2)


def has_hit_obstacle(self, location: Coordinate) -> bool:

    for obstacle in self.parameters.environment.obstacles:
        if distance_between_coordinates(location, obstacle.location) <= obstacle.radius:
            return True

    return False


def has_sufficient_time_elapsed_since_last_shot(self):

    last_fired = self.history.turret.last_fired

    if not last_fired:
        return True

    current_time = self.history.time
    min_firing_interval = self.parameters.turret.min_firing_interval

    return current_time - last_fired >= min_firing_interval


def does_rocket_impact_turret(self):

    target_radius = self.parameters.turret.target_radius
    rocket_location = self.history.rocket.location
    turret_location = self.parameters.turret.location

    return (
        distance_between_coordinates(rocket_location, turret_location) <= target_radius
    )


def does_projectile_impact_rocket(self):

    target_radius = self.parameters.rocket.target_radius
    rocket_location = self.history.rocket.location

    for projectile in self.history.projectiles:
        if not projectile.on_board:
            continue

        projectile_location = projectile.location
        if (
            distance_between_coordinates(rocket_location, projectile_location)
            <= target_radius
        ):
            return True

    return False


def is_rocket_within_bounds(self):

    return is_within_bounds(self, self.history.rocket.location)


def has_rocket_hit_obstacle(self):

    return has_hit_obstacle(self, self.history.rocket.location)


def is_game_time_exceeded(self):

    current_time = self.history.time
    max_game_time = self.parameters.time.max_game_time
    timestep = self.parameters.time.timestep

    return current_time > max_game_time - timestep


def get_engine_force(self, engine):

    if engine == "main":
        return self.history.rocket.main_engine_forces[-1]
    if engine == "left-front":
        return self.history.rocket.left_front_thruster_forces[-1]
    if engine == "left-rear":
        return self.history.rocket.left_rear_thruster_forces[-1]
    if engine == "right-front":
        return self.history.rocket.right_front_thruster_forces[-1]
    if engine == "right-rear":
        return self.history.rocket.right_rear_thruster_forces[-1]

    raise ValueError(f"Engine must be in {self.parameters.animatoion.engine_labels}")


def get_thruster_angle(self, thruster):

    angle = self.history.rocket.angles[-1]

    if thruster in ("left-front", "left-rear"):
        return normalise_angle(angle - math.pi / 2)
    elif thruster in ("right-front", "right-rear"):
        return normalise_angle(angle + math.pi / 2)
    else:
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
            f"thruster must be one of {self.parameters.animation.thruster_labels}"
        )
