import math
import matplotlib.pyplot as plt

from game_data import PolarCoordinate
from math_helpers import normalise_angle

# Remove this
from game_setup import game_data

BARREL_LENGTH = 5.0
ENGINE_BRIDGE_WIDTH = 2.0
PROPULSION_VISUAL_LENGTH = 10.0
PROPULSION_VISUAL_ANGLE = math.pi / 6

ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")


def plot_turret():

    turret_location = game_data.properties.turret_properties.location
    plt.scatter(turret_location.x, turret_location.y, c="b")

    turret_angle = game_data.history.turret_history.angles[-1]
    relative_barrel_tip_location = PolarCoordinate(
        BARREL_LENGTH, turret_angle
    ).pol2cart()

    barrel_tip_location = turret_location + relative_barrel_tip_location

    plt.plot(
        [turret_location.x, barrel_tip_location.x],
        [turret_location.y, barrel_tip_location.y],
        c="b",
    )


def get_rocket_ends():

    rocket_location = game_data.history.rocket_history.locations[-1]

    rocket_angle = game_data.history.rocket_history.angles[-1]
    rocket_length = game_data.properties.rocket_properties.length

    relative_rocket_end = PolarCoordinate(rocket_length / 2, rocket_angle).pol2cart()

    rocket_front_location = rocket_location + relative_rocket_end
    rocket_rear_location = rocket_location - relative_rocket_end

    return rocket_front_location, rocket_rear_location


def get_engine_bridge_ends():

    _, rocket_rear_location = get_rocket_ends()

    rocket_angle = game_data.history.rocket_history.angles[-1]

    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_engine_end = PolarCoordinate(
        ENGINE_BRIDGE_WIDTH / 2, perpendicular_angle
    ).pol2cart()

    engine_bridge_left_location = rocket_rear_location + relative_engine_end
    engine_bridge_right_location = rocket_rear_location - relative_engine_end

    return engine_bridge_left_location, engine_bridge_right_location


def plot_rocket_body():

    rocket_front_location, rocket_rear_location = get_rocket_ends()

    plt.plot(
        [rocket_front_location.x, rocket_rear_location.x],
        [rocket_front_location.y, rocket_rear_location.y],
        c="g",
    )


def plot_engine_bridge():

    engine_bridge_left_location, engine_bridge_right_location = get_engine_bridge_ends()

    plt.plot(
        [engine_bridge_left_location.x, engine_bridge_right_location.x],
        [engine_bridge_left_location.y, engine_bridge_right_location.y],
        c="g",
    )


def plot_propulsion_system():

    for engine in ENGINES:
        plot_engine_strength(engine)


def plot_engine_strength(engine: str):

    rocket_angle = game_data.history.rocket_history.angles[-1]
    max_main_engine_force = game_data.properties.rocket_properties.max_main_engine_force

    if engine == "main":
        force = game_data.history.rocket_history.main_engine_forces[-1]
        _, projection_location = get_rocket_ends()
        angle = normalise_angle(rocket_angle + math.pi)
    elif engine == "left-front":
        force = game_data.history.rocket_history.left_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        angle = normalise_angle(rocket_angle + math.pi / 2)
    elif engine == "left-rear":
        force = game_data.history.rocket_history.left_rear_thruster_forces[-1]
        projection_location, _ = get_engine_bridge_ends()
        angle = normalise_angle(rocket_angle + math.pi / 2)
    elif engine == "right-front":
        force = game_data.history.rocket_history.right_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        angle = normalise_angle(rocket_angle - math.pi / 2)
    elif engine == "right-rear":
        force = game_data.history.rocket_history.right_rear_thruster_forces[-1]
        _, projection_location = get_engine_bridge_ends()
        angle = normalise_angle(rocket_angle - math.pi / 2)
    else:
        raise ValueError(f"Engine must be in {ENGINES}")

    thrust_ratio = force / max_main_engine_force
    edge_length = PROPULSION_VISUAL_LENGTH * thrust_ratio

    left_angle = normalise_angle(angle + PROPULSION_VISUAL_ANGLE)
    relative_thrust_left_location = PolarCoordinate(edge_length, left_angle).pol2cart()
    thrust_left_location = projection_location + relative_thrust_left_location

    right_angle = normalise_angle(angle - PROPULSION_VISUAL_ANGLE)
    relative_thrust_right_location = PolarCoordinate(
        edge_length, right_angle
    ).pol2cart()
    thrust_right_location = projection_location + relative_thrust_right_location

    patch = plt.Polygon(
        [
            list(projection_location),
            list(thrust_left_location),
            list(thrust_right_location),
        ],
        color="r",
    )
    plt.gca().add_patch(patch)


def plot_rocket():

    plot_rocket_body()

    plot_engine_bridge()

    plot_propulsion_system()


def plot_projectiles():

    projectiles = game_data.history.projectile_histories
    for projectile in projectiles:
        if not projectile.on_board:
            continue

        location = projectile.locations[-1]
        plt.scatter(location.x, location.y, c="k")


def set_board_dimensions():

    # Define board edges
    width = game_data.environment.width
    height = game_data.environment.height
    plt.xlim([-width / 2, width / 2])
    plt.ylim([-height / 2, height / 2])

    # Make them proportional
    plt.gca().set_aspect("equal", adjustable="box")


def generate_board():

    set_board_dimensions()

    plot_rocket()

    plot_turret()

    plot_projectiles()

    plt.show()
