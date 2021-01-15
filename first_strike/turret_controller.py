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

    if not can_turret_fire():
        return calc_rotation_velocity(), False

    if will_projectile_hit_rocket():
        return calc_rotation_velocity(), True

    return calc_rotation_velocity(), False


def calc_rotation_velocity():

    max_rotation_speed = game_data.properties.turret_properties.max_rotation_speed
    current_angle = game_data.history.turret_history.angles[-1]

    intercept_angle = (
        calc_intercept_angle()
    )  # Get the angle whose shot would intercept the rocket
    delta_angle = normalise_angle(intercept_angle - current_angle)
    timestep = game_data.environment.timestep
    mag_rotation_speed = min(
        max_rotation_speed, abs(delta_angle) / timestep
    )  # Take a smaller step if a full move would carry past the rocket

    if delta_angle >= 0:
        return mag_rotation_speed
    return -mag_rotation_speed


def calc_intercept_angle():
    """https://math.stackexchange.com/questions/213545/solving-trigonometric-equations-of-the-form-a-sin-x-b-cos-x-c"""
    # TODO: Account for edge case where rocket is flying directly towards/away from turret
    # Actually, logically there will still only be one unique intercept point
    # The only time the lines would be truly the same is if the rocket was:
    # - At the same coordinate as the turret
    # - Travelling at the same velocity as the projectile
    # TODO: Account for case where rocket is directly behind the turret and flying towards it
    # TODO: turret_location.x - rocket_location.x == 0 breaks k, which breaks a lot of other things

    projectile_speed = game_data.properties.turret_properties.projectile_speed
    turret_location = game_data.properties.turret_properties.location

    rocket_velocity = calc_rocket_velocity()
    rocket_location = game_data.history.rocket_history.locations[-1]

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
        return calc_angle2rocket()  # Track the rocket

    def valid_angle(theta):

        try:
            t1 = (turret_location.x - rocket_location.x) / (
                rocket_velocity.x - projectile_speed * math.cos(theta)
            )
            x_equal = False
            x_intercepts = t1 >= 0
        except ZeroDivisionError: # x velocity of rocket and projectile are the same
            x_equal = True  
            x_intercepts = math.isclose(turret_location.x, rocket_location.x)

        try:
            t2 = (turret_location.y - rocket_location.y) / (
                rocket_velocity.y - projectile_speed * math.sin(theta)
            )
            y_equal = False
            y_intercepts = t2 >= 0
        except ZeroDivisionError: # y velocity of rocket and projectile are the same
            y_equal = True  
            y_intercepts = math.isclose(turret_location.y, rocket_location.y)

            return (
                not (x_equal and y_equal)
                and x_intercepts
                and y_intercepts
                and ((x_equal is not y_equal) or math.isclose(t1, t2))
            )

        except ZeroDivisionError:  # Projectile and rocket x or y velocities are the same, can never intersect
            return False

    intercept_angle = normalise_angle(m - beta)
    print(intercept_angle)
    if valid_angle(intercept_angle):
        return intercept_angle
    print(normalise_angle(math.pi - m - beta))
    valid_angle(normalise_angle(math.pi - m - beta))
    return normalise_angle(math.pi - m - beta)

    t1 = turret_location

    return theta


def can_turret_fire():

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
    b = 2 * (x1 * x2 + y1 * y2)
    c = x2 ** 2 + y2 ** 2

    try:
        t_m = -b / (2 * a)  # Find time for local minima
        if t_m < 0:  # If the minimum occurs in the past, set min time to 0
            t_m = 0.0
    except ZeroDivisionError:  # When rocket and projectile have exactly equal velocity
        t_m = 0.0

    smallest_distance = math.sqrt(a * t_m ** 2 + b * t_m + c)

    target_radius = game_data.properties.rocket_properties.target_radius

    return smallest_distance <= target_radius / 2  # Aim for half the radius


def calc_angle2rocket():

    turret_x, turret_y = game_data.properties.turret_properties.location
    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]

    return math.atan2(rocket_y - turret_y, rocket_x - turret_x)
