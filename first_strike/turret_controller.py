import math

from game_setup import game_data
from math_helpers import normalise_angle
from player_controllers.player_rocket_controller import player_rocket_controller


def turret_controller():

    player_controller_inputs = player_rocket_controller()
    if player_controller_inputs is not None:
        return player_controller_inputs

    return default_turret_controller()


def default_turret_controller():

    rotation_speed = game_data.properties.turret_properties.max_rotation_speed

    # Decrease the angle to the rocket
    angle_rocket_rel_to_turret = angle_to_rocket()
    if angle_rocket_rel_to_turret > 0:
        rs = rotation_speed
    else:
        rs = -rotation_speed

    # If sufficient time has elapsed, and rocket is within cone of vision, fire the cannon
    if abs(angle_rocket_rel_to_turret) > math.pi / 6:
        return rs, False

    when_fired = game_data.history.turret_history.when_fired
    if not when_fired:
        return rs, True

    min_firing_interval = game_data.properties.turret_properties.min_firing_interval
    current_time = game_data.history.timesteps[-1]
    last_fired = when_fired[-1]
    fire = current_time - last_fired >= min_firing_interval

    return rs, fire


def angle_to_rocket():

    turret_x, turret_y = game_data.properties.turret_properties.location
    turret_angle = game_data.history.turret_history.angles[-1]
    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]

    angle = math.atan2(rocket_y - turret_y, rocket_x - turret_x)
    return normalise_angle(angle - turret_angle)
