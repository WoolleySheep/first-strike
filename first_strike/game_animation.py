import math
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from game_data import PolarCoordinate
from game_setup import game_data
from generate_board import get_rocket_ends
from math_helpers import normalise_angle
from play import get_inputs, record_inputs, advance_game_data

BOARD_AREA_TO_BARREL_LENGTH_RATIO = 0.05
ROCKET_LENGTH_ENGINE_BRIDGE_RATIO = 0.3
ROCKET_LENGTH_MAX_ENGINE_THRUST_RATIO = 0.7
THRUST_CONE_ANGLE = math.pi / 6
ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")


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

    rocket_length = game_data.properties.rocket_properties.length
    engine_bridge_width = ROCKET_LENGTH_ENGINE_BRIDGE_RATIO * rocket_length

    rocket_angle = game_data.history.rocket_history.angles[-1]

    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_engine_end = PolarCoordinate(
        engine_bridge_width / 2, perpendicular_angle
    ).pol2cart()

    engine_bridge_left_location = rocket_rear_location + relative_engine_end
    engine_bridge_right_location = rocket_rear_location - relative_engine_end

    return engine_bridge_left_location, engine_bridge_right_location

class AnimateGame:
    def __init__(self):
        self.set_up_board()
        self.animation = animation.FuncAnimation(self.fig, self.update, interval=int(game_data.environment.timestep * 1000))

    def set_up_board(self):
        self.fig, self.ax = plt.subplots()

        width = game_data.environment.width
        height = game_data.environment.height

        self.ax.axis([-width / 2, width / 2, -height / 2, height / 2])
        plt.gca().set_aspect("equal", adjustable="box")

        (self.rocket_body,) = self.ax.plot([], c="g")
        self.engine_bridge, = self.ax.plot([], c="g")
        self.main_engine_thrust, = self.ax.plot([], c="r")
        self.left_front_thrust, = self.ax.plot([], c="r")
        self.left_rear_thrust, = self.ax.plot([], c="r")
        self.right_front_thrust, = self.ax.plot([], c="r")
        self.right_rear_thrust, = self.ax.plot([], c="r")

        self.turret_body = self.plot_turret_body()
        self.turret_barrel, = self.ax.plot([], c="b")

        self.projectiles = self.ax.scatter([], [], c="k")

        self.plots = [self.rocket_body, self.engine_bridge, self.main_engine_thrust, self.left_front_thrust, self.left_rear_thrust, self.right_front_thrust, self.right_rear_thrust, self.turret_body, self.turret_barrel, self.projectiles]

    def update(self, i):

        _, rocket_inputs, _, _, turret_inputs, _ = get_inputs()

        record_inputs(rocket_inputs, turret_inputs)

        advance_game_data()

        self.plot_board()

        return self.plots

    def plot_board(self):

        self.update_title()

        self.plot_rocket()
        self.plot_turret()
        self.plot_projectiles()

    def update_title(self):
        
        current_time = game_data.history.timesteps[-1]
        self.ax.set_title(f"game time = {current_time:>5.1f}s")

    def plot_rocket(self):

        self.plot_rocket_body()
        self.plot_engine_bridge()
        self.plot_main_engine_thrust()
        self.plot_left_front_thrust()
        self.plot_left_rear_thrust()
        self.plot_right_front_thrust()
        self.plot_right_rear_thrust()

    def plot_rocket_body(self):

        rocket_front_location, rocket_rear_location = get_rocket_ends()

        self.rocket_body.set_data(
            [rocket_front_location.x, rocket_rear_location.x],
            [rocket_front_location.y, rocket_rear_location.y],
        )

    def plot_engine_bridge(self):

        engine_bridge_left_location, engine_bridge_right_location = get_engine_bridge_ends()

        self.engine_bridge.set_data(
            [engine_bridge_left_location.x, engine_bridge_right_location.x],
            [engine_bridge_left_location.y, engine_bridge_right_location.y],
        )

    def plot_turret(self):

        self.plot_turret_barrel()

    def plot_turret_body(self):

        turret_location = game_data.properties.turret_properties.location
        return self.ax.scatter([turret_location.x], [turret_location.y], c="b")

    def plot_turret_barrel(self):

        barrel_length = BOARD_AREA_TO_BARREL_LENGTH_RATIO * math.sqrt(game_data.environment.board_area)

        turret_location = game_data.properties.turret_properties.location
        turret_angle = game_data.history.turret_history.angles[-1]
        relative_barrel_tip_location = PolarCoordinate(
            barrel_length, turret_angle
        ).pol2cart()

        barrel_tip_location = turret_location + relative_barrel_tip_location

        self.turret_barrel.set_data(
            [turret_location.x, barrel_tip_location.x],
            [turret_location.y, barrel_tip_location.y],
        )

    def plot_projectiles(self):

        projectiles = game_data.history.projectile_histories
        active_projectile_locations = []
        for projectile in projectiles:
            if projectile.on_board:
                location = projectile.locations[-1]
                active_projectile_locations.append(list(location))

        # TODO: Cannot deal with cases where the number of projectiles on 
        # the board drops to 0
        if active_projectile_locations:
            self.projectiles.set_offsets(active_projectile_locations)


    def plot_main_engine_thrust(self):
        
        force = game_data.history.rocket_history.main_engine_forces[-1]
        _, projection_location = get_rocket_ends()
        relative_engine_angle = math.pi
        engine_plot = self.main_engine_thrust

        self._plot_engine_thrust(force, projection_location, relative_engine_angle, engine_plot)

    def plot_left_front_thrust(self):

        force = game_data.history.rocket_history.left_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_front_thrust

        self._plot_engine_thrust(force, projection_location, relative_engine_angle, engine_plot)

    def plot_left_rear_thrust(self):

        force = game_data.history.rocket_history.left_rear_thruster_forces[-1]
        projection_location, _ = get_engine_bridge_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_rear_thrust

        self._plot_engine_thrust(force, projection_location, relative_engine_angle, engine_plot)

    def plot_right_front_thrust(self):

        force = game_data.history.rocket_history.right_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_front_thrust

        self._plot_engine_thrust(force, projection_location, relative_engine_angle, engine_plot)

    def plot_right_rear_thrust(self):

        force = game_data.history.rocket_history.right_rear_thruster_forces[-1]
        _, projection_location = get_engine_bridge_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_rear_thrust

        self._plot_engine_thrust(force, projection_location, relative_engine_angle, engine_plot)




    def _plot_engine_thrust(self, force, projection_location, relative_engine_angle, engine_plot):

        rocket_angle = game_data.history.rocket_history.angles[-1]
        projection_angle = normalise_angle(rocket_angle + relative_engine_angle)

        max_main_engine_force = game_data.properties.rocket_properties.max_main_engine_force
        rocket_length = game_data.properties.rocket_properties.length
        thrust_ratio = force / max_main_engine_force
        edge_length = ROCKET_LENGTH_MAX_ENGINE_THRUST_RATIO * rocket_length * thrust_ratio

        left_angle = normalise_angle(projection_angle + THRUST_CONE_ANGLE)
        relative_thrust_left_location = PolarCoordinate(edge_length, left_angle).pol2cart()
        thrust_left_location = projection_location + relative_thrust_left_location

        right_angle = normalise_angle(projection_angle - THRUST_CONE_ANGLE)
        relative_thrust_right_location = PolarCoordinate(
            edge_length, right_angle
        ).pol2cart()
        thrust_right_location = projection_location + relative_thrust_right_location

        engine_plot.set_data([projection_location.x, thrust_left_location.x, thrust_right_location.x, projection_location.x], [projection_location.y, thrust_left_location.y, thrust_right_location.y, projection_location.y])


game = AnimateGame()
plt.show()
