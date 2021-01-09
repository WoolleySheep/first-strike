import math
import matplotlib.pyplot as plt

from play import pol2cart, normalise_angle

# Remove this
from game_setup import game_data


def generate_board():

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

    # Plot projectiles
    projectiles = game_data.history.projectile_histories
    for projectile in projectiles:
        projectile_x, projectile_y = projectile.locations[-1]
        plt.scatter(projectile_x, projectile_y, c="r")

    # Define board edges
    width = game_data.environment.width
    height = game_data.environment.height
    plt.xlim([-width / 2, width / 2])
    plt.ylim([-height / 2, height / 2])

    # Make them proportional
    plt.gca().set_aspect("equal", adjustable="box")

    # Show the plot (remove this)
    plt.show()


generate_board()
