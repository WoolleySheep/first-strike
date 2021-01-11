import math

from game_data import ProjectileHistory, PolarCoordinate
from game_helpers import (
    is_within_bounds,
    has_sufficient_time_elapsed_since_last_shot,
    does_projectile_impact_rocket,
    does_rocket_impact_turret,
    is_game_time_exceeded,
)
from game_setup import game_data
from generate_board import generate_board
from math_helpers import normalise_angle
from rocket_controller import rocket_controller
from rocket_physics import move_the_rocket
from turret_controller import turret_controller

ROCKET_WIN = 0
TURRET_WIN = 1
DRAW = 2
ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")
THRUSTERS = ENGINES[1:]


def should_fire_a_projectile():

    when_fired = game_data.history.turret_history.when_fired
    current_timestep = game_data.history.timesteps[-1]
    return when_fired and math.isclose(current_timestep, when_fired[-1])


def fire_a_projectile():

    turret_location = game_data.properties.turret_properties.location
    launch_angle = game_data.history.turret_history.angles[-1]
    current_time = game_data.history.timesteps[-1]
    projectile_histories = game_data.history.projectile_histories

    projectile_histories.append(
        ProjectileHistory([turret_location], launch_angle, current_time, True)
    )


def mark_projectiles_off_board():

    projectile_histories = game_data.history.projectile_histories

    for projectile_history in projectile_histories:
        if not projectile_history.on_board:
            continue

        location = projectile_history.locations[-1]
        if not is_within_bounds(location):
            projectile_history.on_board = False


def move_projectiles():

    timestep = game_data.environment.timestep
    projectile_speed = game_data.properties.turret_properties.projectile_speed
    projectile_histories = game_data.history.projectile_histories

    for projectile_history in projectile_histories:
        if not projectile_history.on_board:
            continue

        firing_angle = projectile_history.firing_angle
        locations = projectile_history.locations
        location = locations[-1]
        delta = PolarCoordinate(projectile_speed * timestep, firing_angle).pol2cart()
        locations.append(location + delta)


def rotate_the_turret():

    rotation_velocity = game_data.history.turret_history.rotation_velocities[-1]
    timestep = game_data.environment.timestep

    d_theta = rotation_velocity * timestep

    angles = game_data.history.turret_history.angles
    updated_angle = normalise_angle(angles[-1] + d_theta)
    angles.append(updated_angle)


def update_the_time():

    timesteps = game_data.history.timesteps
    timestep_duration = game_data.environment.timestep
    timesteps.append(timesteps[-1] + timestep_duration)


def advance_game_data():

    move_the_rocket()

    move_projectiles()
    mark_projectiles_off_board()

    if should_fire_a_projectile():
        fire_a_projectile()

    rotate_the_turret()

    update_the_time()


def is_rocket_within_bounds():

    location = game_data.history.rocket_history.locations[-1]
    return is_within_bounds(location)


def validate_inputs(rocket_inputs, turret_inputs):

    rocket_inputs_invalid = (
        len(rocket_inputs) != 5
        or any([type(input_) is not float for input_ in rocket_inputs])
        or not (
            0
            <= rocket_inputs[0]
            <= game_data.properties.rocket_properties.max_main_engine_force
        )
        or any(
            [
                not (
                    0
                    <= input_
                    <= game_data.properties.rocket_properties.max_thruster_force
                )
                for input_ in rocket_inputs[1:]
            ]
        )
    )

    max_rotation_speed = game_data.properties.turret_properties.max_rotation_speed
    turret_inputs_invalid = (
        len(turret_inputs) != 2
        or type(turret_inputs[0]) is not float
        or not (-max_rotation_speed <= turret_inputs[0] <= max_rotation_speed)
        or type(turret_inputs[1]) is not bool
        or (turret_inputs[1] and not has_sufficient_time_elapsed_since_last_shot())
    )

    if rocket_inputs_invalid and turret_inputs_invalid:
        print("Both sets of inputs are invalid")
        return DRAW
    if rocket_inputs_invalid:
        print("Rocket inputs invalid")
        return TURRET_WIN
    if turret_inputs_invalid:
        print("Turret inputs invalid")
        return ROCKET_WIN

    return None


def determine_winner():

    rocket_hit_turret = does_rocket_impact_turret()
    projectile_hit_rocket = does_projectile_impact_rocket()

    if not is_rocket_within_bounds():
        print("The rocket has gone out-of-bounds")
        return TURRET_WIN
    if rocket_hit_turret and projectile_hit_rocket:
        print("The rocket and turret have destroyed each other")
        return DRAW
    if rocket_hit_turret:
        print("The rocket has hit the tower")
        return ROCKET_WIN
    if projectile_hit_rocket:
        print("A projectile has hit the rocket")
        return TURRET_WIN
    if is_game_time_exceeded():
        print("Game time exceeded")
        return DRAW

    return None


def get_inputs():

    rocket_controller_failed = False
    turret_controller_failed = False
    rocket_inputs = None
    turret_inputs = None
    rocket_error = None
    turret_error = None

    try:
        rocket_inputs = rocket_controller()
    except Exception as error:
        rocket_error = error
        rocket_controller_failed = True

    try:
        turret_inputs = turret_controller()
    except Exception as error:
        turret_error = error
        turret_controller_failed = True

    return (
        rocket_controller_failed,
        rocket_inputs,
        rocket_error,
        turret_controller_failed,
        turret_inputs,
        turret_error,
    )


def controller_failure(
    rocket_controller_failed, rocket_error, turret_controller_failed, turret_error
):

    if rocket_controller_failed and turret_controller_failed:
        print("Both controllers failed simultaneously")
        print(f"Rocket error: {rocket_error}")
        print(f"Turret error: {turret_error}")
        return DRAW
    if rocket_controller_failed:
        print("Rocket controller failed")
        print(f"Rocket error: {rocket_error}")
        return TURRET_WIN
    if turret_controller_failed:
        print("Turret controller failed")
        print(f"Turret error: {turret_error}")
        return ROCKET_WIN

    return None


def display_result(result):

    if result == DRAW:
        print("It's a draw!")
    elif result == ROCKET_WIN:
        print("Rocket wins!")
    elif result == TURRET_WIN:
        print("Turret wins!")
    else:
        print("Something has gone wrong...")


def play_first_strike():
    while True:
        (
            rocket_controller_failed,
            rocket_inputs,
            rocket_error,
            turret_controller_failed,
            turret_inputs,
            turret_error,
        ) = get_inputs()

        result = controller_failure(
            rocket_controller_failed,
            rocket_error,
            turret_controller_failed,
            turret_error,
        )
        if result is not None:
            break

        result = validate_inputs(rocket_inputs, turret_inputs)
        if result is not None:
            break

        record_inputs(rocket_inputs, turret_inputs)

        advance_game_data()

        generate_board()

        result = determine_winner()
        if result is not None:
            break

    display_result(result)
