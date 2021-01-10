import math

from game_data import ProjectileHistory, Coordinate, PolarCoordinate
from game_helpers import (
    is_within_bounds,
    has_sufficient_time_elapsed_since_last_shot,
    does_projectile_impact,
    is_game_time_exceeded,
)
from game_setup import game_data
from generate_board import generate_board
from math_helpers import normalise_angle, cart2pol, pol2cart, calc_magnitude
from rocket_controller import rocket_controller
from turret_controller import turret_controller

ROCKET_WIN = 0
TURRET_WIN = 1
DRAW = 2
THRUSTERS = ("left-front", "left-rear", "right-front", "right-rear")


def calc_rocket_velocity():

    locations = game_data.history.rocket_history.locations
    timestep = game_data.environment.timestep

    if len(locations) < 2:
        return Coordinate(0.0, 0.0)

    return (locations[-1] - locations[-2]) / timestep


def calc_rocket_acceleration():

    locations = game_data.history.rocket_history.locations
    timestep = game_data.environment.timestep

    if len(locations) < 3:
        return Coordinate(0.0, 0.0)

    v1 = (locations[-1] - locations[-2]) / timestep
    v2 = (locations[-2] - locations[-3]) / timestep

    return (v1 - v2) / timestep


def calc_rocket_angular_velocity():

    angles = game_data.history.rocket_history.angles
    timestep = game_data.environment.timestep

    if len(angles) < 2:
        return 0.0

    return (angles[-1] - angles[-2]) / timestep


def calc_rocket_angular_acceleration():

    angles = game_data.history.rocket_history.angles
    timestep = game_data.environment.timestep

    if len(angles) < 3:
        return 0.0

    theta_1 = (angles[-1] - angles[-2]) / timestep
    theta2 = (angles[-2] - angles[-3]) / timestep

    return (theta1 - theta2) / timestep


def calc_main_engine_acceleration():

    angle = game_data.history.rocket_history.angles[-1]
    mass = game_data.properties.rocket_properties.mass
    force = game_data.properties.rocket_properties.max_main_engine_force

    f = pol2cart(PolarCoordinate(main_thruster_force, angle))

    return f / mass


def calc_thruster_acceleration(thruster: str) -> Coordinate:

    mass = game_data.properties.rocket_properties.mass
    angle = game_data.history.rocket_history.angles[-1]

    if thruster in ("left-front", "left-rear"):
        thruster_angle = normalise_angle(angle - math.pi / 2)
    elif thruster in ("right-front", "right-rear"):
        thruster_angle = normalise_angle(angle + math.pi / 2)
    else:
        raise ValueError(f"thruster must be one of {THRUSTERS}")

    if thruster == "left-front":
        force = game_data.history.rocket_history.left_front_thruster_forces[-1]
    elif thruster == "left-rear":
        force = game_data.history.rocket_history.left_rear_thruster_forces[-1]
    elif thruster == "right-front":
        force = game_data.history.rocket_history.right_front_thruster_forces[-1]
    else:
        force = game_data.history.rocket_history.right_rear_thruster_forces[-1]

    f = PolarCoordinate(force, thruster_angle).pol2cart()

    return f / mass
 
    
def calc_thruster_angular_acceleration(thruster: str) -> float:

    length = game_data.properties.rocket_properties.length
    moment_of_inertia = game_data.properties.rocket_properties.moment_of_inertia
    mag_torque = force * length / 2
    mag_angular_acc = mag_torque / moment_of_inertia

    if thruster in ("left-front", "right-rear"):
        direction = -1
    elif thruster in ("right-front", "left-rear"):
        direction = 1
    else:
        raise ValueError(f"thruster must be one of {THRUSTERS}")

    return direction * mag_angular_acc

def move_the_rocket():

    timestep = game_data.environment.timestep

    rocket_vel = calc_rocket_velocity()
    rocket_acc = calc_rocket_acceleration(game_data, rocket_vel)
    rocket_ang_vel = calc_rocket_angular_velocity(game_data)
    rocket_ang_acc = calc_rocket_angular_acceleration(game_data, rocket_ang_vel)
    main_engine_acc = calc_main_engine_acceleration(game_data, main_engine_force)
    thrusters_acc = [calc_thruster_acceleration(thruster) for thruster in THRUSTERS]
    thrusters_ang_acc = [calc_angular_thruster_acceleration(thruster) for thruster in THRUSTERS]

    acc = rocket_acc + main_engine_acc + sum(thrusters_acc)
    ang_acc = rocket_ang_acc + sum(thrusters_ang_acc)

    updated_rocket_vel = rocket_vel + acc * timestep
    updated_rocket_ang_vel = rocket_ang_vel + ang_acc * timestep

    rocket_locations = game_data.history.rocket_history.locations
    rocket_locations.append(rocket_locations[-1] + updated_rocket_vel * timestep)

    rocket_angles = game_data.history.rocket_history.angles
    rocket_angles.append(rocket_angles[-1] + updated_rocket_ang_vel * timestep)


def should_fire_a_projectile():

    when_fired = game_data.history.turret_history.when_fired
    current_timestep = game_data.history.timesteps[-1]
    return when_fired and math.isclose(current_timestep, when_fired[-1])

def fire_a_projectile()

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


def advance_projectiles():

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
    angles.append(new_angle)


def update_the_time():

    timesteps = game_data.history.timesteps
    timestep_duration = game_data.properties.timestep
    timesteps.append(timesteps[-1] + timestep_duration)



def advance_game_data():

    move_the_rocket()
    
    advance_projectiles()
    mark_projectiles_off_board()

    if should_fire_a_projectile():
        fire_a_projectile()
        
    rotate_the_turret()
    
    update_the_time()


def distance_between(coord1, coord2):

    return (coord1 - coord2).magnitude()


def does_rocket_impact_turret():

    target_radius = game_data.properties.turret_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]
    turret_location = game_data.properties.turret_properties.location

    return distance_between(rocket_location, turret_location) <= target_radius


def is_rocket_within_bounds():

    location = game_data.history.rocket_history.locations[-1]
    return is_within_bounds(location)


def record_inputs(rocket_inputs, turret_inputs):

    (
        main_engine_force,
        lf_thruster_force,
        lr_thruster_force,
        rf_thruster_force,
        rr_thruster_force,
    ) = rocket_inputs
    rotation_velocity, fired = turret_inputs

    rocket_history = game_data.history.rocket_history
    rocket_history.main_engine_forces.append(main_engine_force)
    rocket_history.left_front_thruster_forces.append(lf_thruster_force)
    rocket_history.left_rear_thruster_forces.append(lr_thruster_force)
    rocket_history.right_front_thruster_forces.append(rf_thruster_force)
    rocket_history.right_rear_thruster_forces.append(rr_thruster_force)

    turret_history = game_data.history.turret_history
    turret_history.rotation_velocities.append(rotation_velocity)
    if fired:
        turret_history.when_fired.append(game_data.history.timesteps[-1])


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

    rocket_win = does_rocket_impact_turret()
    turret_win = does_projectile_impact_rocket() or not is_rocket_within_bounds()

    if rocket_win and turret_win:
        return DRAW
    if rocket_win:
        ROCKET_WIN
    if turret_win:
        TURRET_WIN
    
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

def controller_failure(rocket_controller_failed, rocket_error, turret_controller_failed, turret_error):
        
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

def display_result(result)
        
        if result == DRAW:
            print("It's a draw!")
        if result == ROCKET_WIN:
            print("Rocket wins!")
        if result == TURRET_WIN:
            print("Turret wins!")

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

        result = controller_failure(rocket_controller_failed, rocket_error, turret_controller_failed, turret_error)
        if result is not None:
            break


        result = validate_inputs(rocket_inputs, turret_inputs)
        if result is not None:
            break

        record_inputs(rocket_inputs, turret_inputs)

        advance_game_data()

        generate_board()

        rocket_win, turret_win = determine_winner()

        result = determine_winner()
        if result is not None:
            break
    
    display_result()




print(play_first_strike())
