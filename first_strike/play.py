import math

from game_data import ProjectileHistory
from game_helpers import is_within_bounds, has_sufficient_time_elapsed_since_last_shot, does_projectile_impact, is_game_time_exceeded
from game_setup import game_data
from generate_board import generate_board
from math_helpers import normalise_angle, cart2pol, pol2cart, calc_magnitude
from rocket_controller import rocket_controller
from turret_controller import turret_controller

ROCKET_WIN = 0
TURRET_WIN = 1
DRAW = 2

def calc_velocity(game_data):

    locations = game_data.history.rocket_history.locations
    timestep = game_data.environment.timestep

    if len(locations) < 2:
        return 0.0, 0.0

    vx = (locations[-1][0] - locations[-2][0]) / timestep
    vy = (locations[-1][1] - locations[-2][1]) / timestep

    return vx, vy


def calc_acceleration(game_data, v1):

    locations = game_data.history.rocket_history.locations
    timestep = game_data.environment.timestep

    if len(locations) < 3:
        return 0.0, 0.0

    v2x = (locations[-2][0] - locations[-3][0]) / timestep
    v2y = (locations[-2][1] - locations[-3][1]) / timestep

    v1x, v1y = v1

    ax = (v1x - v2x) / timestep
    ay = (v1y - v2y) / timestep

    return ax, ay


def calc_angular_velocity(game_data):

    angles = game_data.history.rocket_history.angles
    timestep = game_data.environment.timestep

    if len(angles) < 2:
        return 0.0

    return (angles[-1] - angles[-2]) / timestep


def calc_angular_acceleration(game_data, theta1):

    angles = game_data.history.rocket_history.angles
    timestep = game_data.environment.timestep

    if len(angles) < 3:
        return 0.0

    theta2 = (angles[-2] - angles[-3]) / timestep

    return (theta1 - theta2) / timestep


def calc_main_engine_acceleration(game_data, main_thruster_force):

    angle = game_data.history.rocket_history.angles[-1]
    mass = game_data.properties.rocket_properties.mass

    fx, fy = pol2cart(main_thruster_force, angle)

    return fx / mass, fy / mass


def calc_thruster_acceleration(game_data, side, force):

    mass = game_data.properties.rocket_properties.mass
    angle = game_data.history.rocket_history.angles[-1]
    if side == "left":
        thruster_angle = normalise_angle(angle - math.pi / 2)
    else:
        thruster_angle = normalise_angle(angle + math.pi / 2)
    force_x, force_y = pol2cart(force, thruster_angle)
    return force_x / mass, force_y / mass


def calc_thruster_angular_acceleration(game_data, rotation, force):

    length = game_data.properties.rocket_properties.length
    torque = force * length / 2
    moment_of_inertia = game_data.properties.rocket_properties.moment_of_inertia
    angular_acc = torque / moment_of_inertia

    if rotation == "clockwise":
        return -angular_acc
    return angular_acc


def remove_out_of_bounds_projectiles(game_data):

    projectile_histories = game_data.history.projectile_histories
    width = game_data.environment.width
    height = game_data.environment.height

    new_projectile_histories = []
    for projectile_history in projectile_histories:
        x, y = projectile_history.locations[-1]
        if is_within_bounds(width, height, x, y):
            new_projectile_histories.append(projectile_history)

    game_data.history.projectile_histories = new_projectile_histories


def advance_projectiles(game_data):

    timestep = game_data.environment.timestep
    projectile_speed = game_data.properties.turret_properties.projectile_speed
    projectile_histories = game_data.history.projectile_histories

    for projectile_history in projectile_histories:
        projectile_locations = projectile_history.locations
        x, y = projectile_locations[-1]
        d_x, d_y = pol2cart(projectile_speed * timestep, projectile_history.angle)
        projectile_locations.append((x + d_x, y + d_y))



def advance_game_data():

    # Unpack inputs
    main_engine_force = game_data.history.rocket_history.main_engine_forces[-1]
    left_front_thruster_force = game_data.history.rocket_history.left_front_thruster_forces[-1]
    left_rear_thruster_force = game_data.history.rocket_history.left_rear_thruster_forces[-1]
    right_front_thruster_force = game_data.history.rocket_history.right_front_thruster_forces[-1]
    right_rear_thruster_force = game_data.history.rocket_history.right_rear_thruster_forces[-1]
    rotation_velocity = game_data.history.turret_history.rotation_velocities[-1]
    
    when_fired = game_data.history.turret_history.when_fired
    current_timestep = game_data.history.timesteps[-1]
    fire = when_fired and math.isclose(current_timestep, when_fired[-1])

    timestep = game_data.environment.timestep

    # Rocket
    rocket_vel = calc_velocity(game_data)
    rocket_acc = calc_acceleration(game_data, rocket_vel)
    rocket_ang_vel = calc_angular_velocity(game_data)
    rocket_ang_acc = calc_angular_acceleration(game_data, rocket_ang_vel)
    main_engine_acc = calc_main_engine_acceleration(game_data, main_engine_force)
    left_front_thruster_acc = calc_thruster_acceleration(
        game_data, "left", left_front_thruster_force
    )
    left_rear_thruster_acc = calc_thruster_acceleration(
        game_data, "left", left_rear_thruster_force
    )
    right_front_thruster_acc = calc_thruster_acceleration(
        game_data, "right", right_front_thruster_force
    )
    right_rear_thruster_acc = calc_thruster_acceleration(
        game_data, "right", right_rear_thruster_force
    )
    left_front_thruster_ang_acc = calc_thruster_angular_acceleration(
        game_data, "clockwise", left_front_thruster_force
    )
    left_rear_thruster_ang_acc = calc_thruster_angular_acceleration(
        game_data, "anti-clockwise", left_rear_thruster_force
    )
    right_front_thruster_ang_acc = calc_thruster_angular_acceleration(
        game_data, "anti-clockwise", right_front_thruster_force
    )
    right_rear_thruster_ang_acc = calc_thruster_angular_acceleration(
        game_data, "clockwise", right_rear_thruster_force
    )

    a_x = (
        rocket_acc[0]
        + main_engine_acc[0]
        + left_front_thruster_acc[0]
        + left_rear_thruster_acc[0]
        + right_front_thruster_acc[0]
        + right_rear_thruster_acc[0]
    )
    a_y = (
        rocket_acc[1]
        + main_engine_acc[1]
        + left_front_thruster_acc[1]
        + left_rear_thruster_acc[1]
        + right_front_thruster_acc[1]
        + right_rear_thruster_acc[1]
    )
    a_theta = (
        rocket_ang_acc
        + left_front_thruster_ang_acc
        + left_rear_thruster_ang_acc
        + right_front_thruster_ang_acc
        + right_rear_thruster_ang_acc
    )

    v_x, v_y = rocket_vel
    new_v_x = v_x + a_x * timestep
    new_v_y = v_y + a_y * timestep
    new_v_theta = rocket_ang_vel + a_theta * timestep

    locations = game_data.history.rocket_history.locations
    x, y = locations[-1]
    locations.append((x + new_v_x * timestep, y + new_v_y * timestep))

    angles = game_data.history.rocket_history.angles
    angles.append(normalise_angle(angles[-1] + new_v_theta * timestep))

    # Existing projectiles
    advance_projectiles(game_data)
    remove_out_of_bounds_projectiles(game_data)

    # New projectile
    if fire:
        turret_location = game_data.properties.turret_properties.location
        angle = game_data.history.turret_history.angles[-1]
        current_time = game_data.history.timesteps[-1]
        projectile_histories = game_data.history.projectile_histories

        projectile_histories.append(
            ProjectileHistory([turret_location], angle, current_time)
        )

    # Turret
    d_theta = rotation_velocity * timestep
    angles = game_data.history.turret_history.angles
    new_angle = normalise_angle(angles[-1] + d_theta)
    angles.append(new_angle)

    # Other
    timesteps = game_data.history.timesteps
    timesteps.append(timesteps[-1] + timestep)


def distance_between(loc1, loc2):

    x1, y1 = loc1
    x2, y2 = loc2

    return calc_magnitude(x2 - x1, y2 - y1)


def does_rocket_impact():

    target_radius = game_data.properties.turret_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]
    turret_location = game_data.properties.turret_properties.location

    return distance_between(rocket_location, turret_location) <= target_radius



def is_rocket_within_bounds(game_data):

    x, y = game_data.history.rocket_history.locations[-1]
    return is_within_bounds(x, y)


def record_inputs(rocket_inputs, turret_inputs):

    main_engine_force, lf_thruster_force, lr_thruster_force, rf_thruster_force, rr_thruster_force = rocket_inputs
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
            or not (0 <= rocket_inputs[0] <= game_data.properties.rocket_properties.max_main_engine_force)
            or any([not (0 <= input_ <= game_data.properties.rocket_properties.max_thruster_force) for input_ in rocket_inputs[1:]])
        )
        
        max_rotation_speed = game_data.properties.turret_properties.max_rotation_speed
        turret_inputs_invalid = (
            len(turret_inputs) != 2
            or type(turret_inputs[0]) is not float
            or not (-max_rotation_speed <= turret_inputs[0] <= max_rotation_speed)
            or type(turret_inputs[1]) is not bool
            or (turret_inputs[1] and not has_sufficient_time_elapsed_since_last_shot())
        )

        return rocket_inputs_invalid, turret_inputs_invalid

def determine_winner():

    rocket_win = does_rocket_impact()
    turret_win = does_projectile_impact() or not is_rocket_within_bounds(game_data)

    return rocket_win, turret_win

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
    
    return rocket_controller_failed, rocket_inputs, rocket_error, turret_controller_failed, turret_inputs, turret_error




def play_first_strike():
    while True:
        rocket_controller_failed, rocket_inputs, rocket_error, turret_controller_failed, turret_inputs, turret_error = get_inputs()

        # Check if either controller failed
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

        rocket_inputs_invalid, turret_inputs_invalid = validate_inputs(rocket_inputs, turret_inputs)

        if rocket_inputs_invalid and turret_inputs_invalid:
            print("Both sets of inputs are invalid")
            return DRAW
        if rocket_inputs_invalid:
            print("Rocket inputs invalid")
            return TURRET_WIN
        if turret_inputs_invalid:
            print("Turret inputs invalid")
            return ROCKET_WIN

        record_inputs(rocket_inputs, turret_inputs)

        advance_game_data()

        generate_board(rocket_inputs)

        rocket_win, turret_win = determine_winner()

        if (rocket_win and turret_win) or is_game_time_exceeded():
            return DRAW
        if rocket_win:
            return ROCKET_WIN
        if turret_win:
            return TURRET_WIN


print(play_first_strike())
