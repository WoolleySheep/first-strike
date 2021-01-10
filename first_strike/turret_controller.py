import math

from game_setup import game_data
from math_helpers import normalise_angle

def turret_controller():

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

    firing_interval = game_data.properties.turret_properties.firing_interval
    current_time = game_data.history.timesteps[-1]
    last_fired = when_fired[-1]
    fire = current_time - last_fired >= firing_interval

    return rs, fire

def angle_to_rocket():

    turret_x, turret_y = game_data.properties.turret_properties.location
    turret_angle = game_data.history.turret_history.angles[-1]
    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]

    angle = math.atan2(rocket_y - turret_y, rocket_x - turret_x)
    return normalise_angle(angle - turret_angle)
