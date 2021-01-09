import math

from game_data import ProjectileHistory
from game_setup import game_data
from rocket_controller import rocket_controller
from turret_controller import turret_controller

ROCKET_WIN = 0
TURRET_WIN = 1
DRAW = 2


def cart2pol(x, y):

    r = calc_magnitude(x, y)
    theta = math.atan2(y, x)

    return r, theta


def pol2cart(r, theta):

    x = r * math.cos(theta)
    y = r * math.sin(theta)

    return x, y


def calc_magnitude(x, y):

    return math.sqrt(x ** 2 + y ** 2)


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
            new_projectile_histories.projectile_history

    game_data.history.projectile_histories = new_projectile_histories


def advance_projectiles(game_data):

    timestep = game_data.environment.timestep
    projectile_speed = game_data.properties.turret_properties.projectile_speed
    projectile_histories = game_data.history.projectile_histories

    for projectile_history in projectile_histories:
        x, y = projectile_history.locations[-1]
        d_x, d_y = pol2cart(projectile_speed * timestep, projectile_history.angle)
        projectile_history.append(x + d_x, y + d_y)


def normalise_angle(angle):

    if angle > math.pi:
        return angle - 2 * math.pi
    if angle <= -math.pi:
        return angle + 2 * math.pi
    return angle


def advance_game_data(rocket_inputs, turret_inputs):

    # Unpack inputs
    (
        main_engine_force,
        left_front_thruster_force,
        left_rear_thruster_force,
        right_front_thruster_force,
        right_rear_thruster_force,
    ) = rocket_inputs
    rotation_speed, fire = turret_inputs

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
    angles.append(angles[-1] + new_v_theta * timestep)

    # Existing projectiles
    advance_projectiles(game_data)
    remove_out_of_bounds_projectiles(game_data)

    # New projectile
    if fire:
        current_timestep = game_data.history.timesteps[-1]
        when_fired = game_data.history.turret_history.when_fired
        when_fired.append(current_timestep)

        turret_location = game_data.properties.turret_properties.location
        angle = game_data.history.turret_history.angles[-1]
        current_time = game_data.history.timesteps[-1]
        projectile_histories = game_data.history.projectile_histories

        projectile_histories.append(
            ProjectileHistory([turret_location], angle, current_time)
        )

    # Turret
    d_theta = rotation_speed * timestep
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


def does_rocket_impact(game_data):

    target_radius = game_data.properties.turret_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]
    turret_location = game_data.properties.turret_properties.location

    return distance_between(rocket_location, turret_location) <= target_radius


def does_projectile_impact(game_data):

    target_radius = game_data.properties.rocket_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]
    projectile_locations = [
        projectile.locations[-1]
        for projectile in game_data.history.projectile_histories
    ]

    return any(
        [
            distance_between(rocket_location, projectile_location) <= target_radius
            for projectile_location in projectile_locations
        ]
    )


def is_rocket_within_bounds(game_data):

    x, y = game_data.history.rocket_history.locations[-1]
    width = game_data.environment.width
    height = game_data.environment.height

    return is_within_bounds(width, height, x, y)


def is_within_bounds(w, h, x, y):

    return -w / 2 <= x <= w / 2 and -h / 2 <= y <= h / 2


def sufficient_time_elapsed_between_shots(game_data):

    when_fired = game_data.history.turret_history.when_fired

    if not when_fired:
        return True

    current_time = game_data.environment.timesteps[-1]
    firing_interval = game_data.properties.turret_properties.firing_interval

    return current_time - when_fired[-1] >= firing_interval


def play_first_strike():
    while True:
        rocket_controller_failed = False
        turret_controller_failed = False
        rocket_error = None
        turret_error = None
        try:
            rocket_inputs = rocket_controller(game_data)
        except Exception as error:
            rocket_error = error
            rocket_controller_failed = True
        try:
            turret_inputs = turret_controller(game_data)
        except Exception as error:
            turret_error = error
            turret_controller_failed = True

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

        # Check if either controller returned invalid inputs
        rocket_inputs_invalid = (
            len(rocket_inputs) != 5
            or any([type(input_) is not float for input_ in rocket_inputs])
            or any([input_ < 0 for input_ in rocket_inputs])
        )
        turret_inputs_invalid = (
            len(turret_inputs) != 2
            or type(turret_inputs[0]) is not float
            or not (-math.pi < turret_inputs[0] <= math.pi)
            or type(turret_inputs[1]) is not bool
            or not sufficient_time_elapsed_between_shots(game_data)
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

        advance_game_data(rocket_inputs, turret_inputs)

        rocket_win = does_rocket_impact(game_data)
        turret_win = does_projectile_impact(game_data) or not is_rocket_within_bounds(
            game_data
        )
        playtime_exceeded = (
            game_data.history.timesteps[-1]
            > game_data.environment.max_playtime - game_data.environment.timestep
        )

        if (rocket_win and turret_win) or playtime_exceeded:
            return DRAW
        if rocket_win:
            return ROCKET_WIN
        if turret_win:
            return TURRET_WIN


print(play_first_strike())
