import math
import matplotlib.pyplot as plt

from game_data import Coordinate, PolarCoordinate
from math_helpers import pol2cart, normalise_angle

# Remove this
from game_setup import game_data

BARREL_LENGTH = 5.0
THRUSTER_BRIDGE_WIDTH = 2.0
PROPULSION_VISUAL_LENGTH = 10.0

def plot_turret():

    turret_location = game_data.properties.turret_properties.location
    plt.scatter(turret_location.x, turret_location.y, c="b")

    turret_angle = game_data.history.turret_history.angles[-1]
    relative_barrel_tip_location = PolarCoordinate(BARREL_LENGTH, turret_angle).pol2cart()

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




def plot_rocket_body():

    rocket_front_location, rocket_rear_location = get_rocket_ends()

    plt.plot(
        [rocket_front_location.x, rocket_rear_location.x,
        [rocket_front_location.y, rocket_rear_location.y,
        c="g",
    )

    return rocket_rear_location


def plot_thruster_bridge():

    _, rocket_rear_location = get_rocket_ends()

    rocket_angle = game_data.history.rocket_history.angles[-1]

    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_thruster_end = PolarCoordinate(THRUSTER_BRIDGE_WIDTH / 2, perpendicular_angle).pol2cart()

    thruster_left_location = rocket_rear_location + relative_thruster_end
    thruster_right_location = rocket_rear_location - relative_thruster_end
    
    plt.plot(
        [thruster_left_location.x, thruster_right_location.x],
        [thruster_left_location.x, thruster_right_location.x],
        c="g",
    )

def plot_propulsion_system():

    rocket_front_location, rocket_rear_location = get_rocket_ends()

    rocket_angle = game_data.history.rocket_history.angles[-1]
    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)

    # Plot main engine
    
    plot_thruster_strength(
        rocket_inputs[0], rocket_rear_location, normalise_angle(rocket_angle - math.pi)
    )

    # Plot thrusters
    plot_thruster_strength(rocket_inputs[1], rocket_front_location, perpendicular_angle)
    plot_propulsion_system(
        rocket_inputs[2], thruster_left_location, perpendicular_angle
    )
    plot_thruster_strength(
        rocket_inputs[3],
        rocket_front_location,
        normalise_angle(perpendicular_angle - math.pi),
    )
    plot_thruster_strength(
        rocket_inputs[4],
        thruster_right_location,
        normalise_angle(perpendicular_angle - math.pi),
    )

def plot_rocket():

    plot_rocket_body()

    plot_thruster_bridge()

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

    plot_rocket()

    plot_turret()

    plot_projectiles()

    set_board_dimensions()

    plt.show()


def plot_thruster_strength(force, projection_location, direction_angle):

    max_main_engine_force = game_data.properties.rocket_properties.max_main_engine_force

    thrust_ratio = force / max_main_engine_force
    edge_length = PROPULSION_VISUAL_LENGTH * thrust_ratio

    left_angle = normalise_angle(direction_angle + math.pi / 6)
    rel_left_location = pol2cart(edge_length, left_angle)
    left_location = (
        projection_location[0] + rel_left_location[0],
        projection_location[1] + rel_left_location[1],
    )

    right_angle = normalise_angle(direction_angle - math.pi / 6)
    rel_right_location = pol2cart(edge_length, right_angle)
    right_location = (
        projection_location[0] + rel_right_location[0],
        projection_location[1] + rel_right_location[1],
    )

    patch = plt.Polygon(
        [list(projection_location), list(left_location), list(right_location)],
        color="r",
    )
    plt.gca().add_patch(patch)
