import math

from game_data import Coordinate, PolarCoordinate
from game_setup import game_data
from math_helpers import normalise_angle, distance_between_coordinates

ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")


def is_within_bounds(location: Coordinate) -> bool:

    w = game_data.environment.width
    h = game_data.environment.height

    return (-w / 2 <= location.x <= w / 2) and (-h / 2 <= location.y <= h / 2)


def has_sufficient_time_elapsed_since_last_shot():

    when_fired = game_data.history.turret_history.when_fired

    if not when_fired:
        return True

    current_time = game_data.history.timesteps[-1]
    min_firing_interval = game_data.properties.turret_properties.min_firing_interval

    return current_time - when_fired[-1] >= min_firing_interval


def does_rocket_impact_turret():

    target_radius = game_data.properties.turret_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]
    turret_location = game_data.properties.turret_properties.location

    return (
        distance_between_coordinates(rocket_location, turret_location) <= target_radius
    )


def does_projectile_impact_rocket():

    target_radius = game_data.properties.rocket_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]

    for projectile_history in game_data.history.projectile_histories:
        if not projectile_history.on_board:
            continue

        projectile_location = projectile_history.locations[-1]
        if (
            distance_between_coordinates(rocket_location, projectile_location)
            <= target_radius
        ):
            return True

    return False


def is_game_time_exceeded():

    current_time = game_data.history.timesteps[-1]
    max_game_time = game_data.environment.max_game_time
    timestep = game_data.environment.timestep

    return current_time > max_game_time - timestep


def get_engine_force(engine):

    if engine == "main":
        return game_data.history.rocket_history.main_engine_forces[-1]
    if engine == "left-front":
        return game_data.history.rocket_history.left_front_thruster_forces[-1]
    if engine == "left-rear":
        return game_data.history.rocket_history.left_rear_thruster_forces[-1]
    if engine == "right-front":
        return game_data.history.rocket_history.right_front_thruster_forces[-1]
    if engine == "right-rear":
        return game_data.history.rocket_history.right_rear_thruster_forces[-1]

    raise ValueError(f"Engine must be in {ENGINES}")


def get_thruster_angle(thruster):

    angle = game_data.history.rocket_history.angles[-1]

    if thruster in ("left-front", "left-rear"):
        return normalise_angle(angle - math.pi / 2)
    elif thruster in ("right-front", "right-rear"):
        return normalise_angle(angle + math.pi / 2)
    else:
        raise ValueError(f"thruster must be one of {ENGINES[1:]}")
    