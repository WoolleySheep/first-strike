import math

from game_setup import game_data
from math_helpers import normalise_angle
from player_controllers.player_rocket_controller import player_rocket_controller
from rocket_physics import calc_rocket_velocity


def turret_controller():

    player_controller_inputs = player_rocket_controller()
    if player_controller_inputs is not None:
        return player_controller_inputs

    return default_turret_controller()


def default_turret_controller():

    if not has_min_firing_interval_elapsed():
        return calc_rotation_velocity(), False
    
    if will_projectile_hit_rocket():
        return calc_rotation_velocity(), True
    
    return calc_rotation_velocity(), False


def calc_rotation_velocity():

    max_rotation_speed = game_data.properties.turret_properties.max_rotation_speed
    current_angle = game_data.history.turret_history.angles[-1]

    intercept_angle = calc_intercept_angle()    # Get the angle whose shot would intercept the rocket
    delta_angle = normalise_angle(intercept_angle - current_angle)
    timestep = game_data.environment.timestep
    mag_rotation_speed = min(max_rotation_speed, abs(delta_angle) / timestep)    # Take a smaller step if a full move would carry past the rocket
    
    if delta_angle >= 0:
        return mag_rotation_speed
    return -mag_rotation_speed



def calc_intercept_angle():
    """https://math.stackexchange.com/questions/213545/solving-trigonometric-equations-of-the-form-a-sin-x-b-cos-x-c"""
    # TODO: Get this working

    projectile_speed = game_data.properties.turret_properties.projectile_speed
    turret_location = game_data.properties.turret_properties.location
    turret_angle = game_data.history.turret_history.angles[-1]

    rocket_velocity = calc_rocket_velocity()
    rocket_location = game_data.history.rocket_history.locations[-1]

    a = 1
    b = (turret_location.y - rocket_location.y) / (turret_location.x - rocket_location.x)
    c = ((b * rocket_velocity.x) - rocket_velocity.y) / projectile_speed

    A = a / math.sqrt(a ** 2 + b ** 2)
    beta = math.acos(A)

    theta = math.asin(c / math.sqrt(a ** 2 + b ** 2)) - beta
    return theta


def has_min_firing_interval_elapsed():

    when_fired = game_data.history.turret_history.when_fired

    if not when_fired:
        return True

    min_firing_interval = game_data.properties.turret_properties.min_firing_interval
    current_time = game_data.history.timesteps[-1]
    last_fired = when_fired[-1]
    
    return current_time - last_fired >= min_firing_interval



def will_projectile_hit_rocket():

    projectile_speed = game_data.properties.turret_properties.projectile_speed
    turret_location = game_data.properties.turret_properties.location
    turret_angle = game_data.history.turret_history.angles[-1]

    rocket_velocity = calc_rocket_velocity()
    rocket_location = game_data.history.rocket_history.locations[-1]

    x1 = rocket_velocity.x - projectile_speed * math.cos(turret_angle)
    x2 = rocket_location.x - turret_location.x
    y1 = rocket_velocity.y - projectile_speed * math.sin(turret_angle)
    y2 = rocket_location.y - turret_location.y

    a = x1 ** 2 + y1 ** 2
    b = x1 * x2 + y1 * y2
    c = x2 ** 2 + y2 ** 2

    t_m = - b / (2 * a)
    smallest_distance = math.sqrt(a * t_m ** 2 + b * t_m + c)
    print("Smallest distance: ", smallest_distance)

    target_radius = game_data.properties.rocket_properties.target_radius

    return smallest_distance <= target_radius / 2   # Aim for half the radius


