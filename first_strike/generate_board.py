import math
import matplotlib.pyplot as plt

from math_helpers import pol2cart, normalise_angle

# Remove this
from game_setup import game_data


def generate_board(rocket_inputs):

    # Plot turret
    turret_x, turret_y = game_data.properties.turret_properties.location
    plt.scatter(turret_x, turret_y, c="b")
    turret_angle = game_data.history.turret_history.angles[-1]
    barrel_length = 5.0
    relative_barrel_location = pol2cart(5.0, turret_angle)
    absolute_barrel_location = (
        relative_barrel_location[0] + turret_x,
        relative_barrel_location[1] + turret_y,
    )
    plt.plot(
        [turret_x, absolute_barrel_location[0]],
        [turret_y, absolute_barrel_location[1]],
        c="b",
    )

    # Plot rocket
    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]
    rocket_angle = game_data.history.rocket_history.angles[-1]
    rocket_length = game_data.properties.rocket_properties.length
    relative_rocket_end = pol2cart(rocket_length / 2, rocket_angle)
    rocket_front_location = (
        rocket_x + relative_rocket_end[0],
        rocket_y + relative_rocket_end[1],
    )
    rocket_rear_location = (
        rocket_x - relative_rocket_end[0],
        rocket_y - relative_rocket_end[1],
    )
    plt.plot(
        [rocket_front_location[0], rocket_rear_location[0]],
        [rocket_front_location[1], rocket_rear_location[1]],
        c="g",
    )
    thruster_width = 2.0
    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_thruster_end = pol2cart(thruster_width / 2, perpendicular_angle)
    thruster_left_location = (
        rocket_rear_location[0] + relative_thruster_end[0],
        rocket_rear_location[1] + relative_thruster_end[1],
    )
    thruster_right_location = (
        rocket_rear_location[0] - relative_thruster_end[0],
        rocket_rear_location[1] - relative_thruster_end[1],
    )
    plt.plot(
        [thruster_left_location[0], thruster_right_location[0]],
        [thruster_left_location[1], thruster_right_location[1]],
        c="g",
    )

    
    # Plot main engine
    plot_propulsion_system(rocket_inputs[0], rocket_rear_location, normalise_angle(rocket_angle - math.pi))
    
    # Plot thrusters
    plot_propulsion_system(rocket_inputs[1], rocket_front_location, perpendicular_angle)
    plot_propulsion_system(rocket_inputs[2], thruster_left_location, perpendicular_angle)
    plot_propulsion_system(rocket_inputs[3], rocket_front_location, normalise_angle(perpendicular_angle - math.pi))
    plot_propulsion_system(rocket_inputs[4], thruster_right_location, normalise_angle(perpendicular_angle - math.pi))


    # Plot projectiles
    projectiles = game_data.history.projectile_histories
    for projectile in projectiles:
        projectile_x, projectile_y = projectile.locations[-1]
        plt.scatter(projectile_x, projectile_y, c="k")

    # Define board edges
    width = game_data.environment.width
    height = game_data.environment.height
    plt.xlim([-width / 2, width / 2])
    plt.ylim([-height / 2, height / 2])

    # Make them proportional
    plt.gca().set_aspect("equal", adjustable="box")

    # Show the plot (remove this)
    plt.show()

def plot_propulsion_system(force, projection_location, direction_angle):

    max_length = 10
    max_main_engine_force = game_data.properties.rocket_properties.max_main_engine_force

    thrust_ratio = force / max_main_engine_force
    edge_length = max_length * thrust_ratio

    left_angle = normalise_angle(direction_angle + math.pi / 6)
    rel_left_location = pol2cart(edge_length, left_angle)
    left_location = projection_location[0] + rel_left_location[0], projection_location[1] + rel_left_location[1]
    
    right_angle = normalise_angle(direction_angle - math.pi / 6)
    rel_right_location = pol2cart(edge_length, right_angle)
    right_location = projection_location[0] + rel_right_location[0], projection_location[1] + rel_right_location[1]

    patch = plt.Polygon([list(projection_location), list(left_location), list(right_location)], color="r")
    plt.gca().add_patch(patch)

