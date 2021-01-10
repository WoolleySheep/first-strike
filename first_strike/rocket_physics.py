from game_data import Coordinate, PolarCoordinate
from game_helpers import get_engine_force, get_thruster_angle
from game_setup import game_data

ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")
THRUSTERS = ENGINES[1:]


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

    theta1 = (angles[-1] - angles[-2]) / timestep
    theta2 = (angles[-2] - angles[-3]) / timestep

    return (theta1 - theta2) / timestep


def calc_main_engine_acceleration():

    angle = game_data.history.rocket_history.angles[-1]
    mass = game_data.properties.rocket_properties.mass
    force = game_data.properties.rocket_properties.max_main_engine_force

    f = PolarCoordinate(force, angle).pol2cart()

    return f / mass


def calc_thruster_acceleration(thruster: str) -> Coordinate:

    mass = game_data.properties.rocket_properties.mass

    force = get_engine_force(thruster)
    angle = get_thruster_angle(thruster)

    f = PolarCoordinate(force, angle).pol2cart()

    return f / mass


def calc_thruster_angular_acceleration(thruster: str) -> float:

    length = game_data.properties.rocket_properties.length
    moment_of_inertia = game_data.properties.rocket_properties.moment_of_inertia

    force = get_engine_force(thruster)

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
    rocket_acc = calc_rocket_acceleration()
    rocket_ang_vel = calc_rocket_angular_velocity()
    rocket_ang_acc = calc_rocket_angular_acceleration()
    main_engine_acc = calc_main_engine_acceleration()
    thrusters_acc = [calc_thruster_acceleration(thruster) for thruster in THRUSTERS]
    thrusters_ang_acc = [
        calc_thruster_angular_acceleration(thruster) for thruster in THRUSTERS
    ]

    acc = rocket_acc + main_engine_acc + sum(thrusters_acc)
    ang_acc = rocket_ang_acc + sum(thrusters_ang_acc)

    updated_rocket_vel = rocket_vel + acc * timestep
    updated_rocket_ang_vel = rocket_ang_vel + ang_acc * timestep

    rocket_locations = game_data.history.rocket_history.locations
    rocket_locations.append(rocket_locations[-1] + updated_rocket_vel * timestep)

    rocket_angles = game_data.history.rocket_history.angles
    rocket_angles.append(rocket_angles[-1] + updated_rocket_ang_vel * timestep)
