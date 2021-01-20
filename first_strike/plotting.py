import math
import matplotlib.pyplot as plt

from coordinate_classes import PolarCoordinate
from math_helpers import normalise_angle


class Plotting:
    def __init__(self, parameters, history, controllers):
        self.parameters = parameters
        self.history = history
        self.controllers = controllers
        self.title = parameters.animation.default_title
        self.alpha = 1.0
        self.fig, (self.ax, self.ax2) = plt.subplots(
            1, 2, gridspec_kw={"width_ratios": [5, 1]}
        )

        self.obstacles = self.plot_obstacles()

        (self.rocket_body,) = self.ax.plot([], c="g")
        (self.engine_bridge,) = self.ax.plot([], c="g")
        (self.main_engine_thrust,) = self.ax.plot([], c="r")
        (self.left_front_thrust,) = self.ax.plot([], c="r")
        (self.left_rear_thrust,) = self.ax.plot([], c="r")
        (self.right_front_thrust,) = self.ax.plot([], c="r")
        (self.right_rear_thrust,) = self.ax.plot([], c="r")

        self.turret_body = self.plot_turret_body()
        (self.turret_barrel,) = self.ax.plot([], c="b")

        self.projectiles = self.ax.scatter([], [], c="k")

        (self.charging,) = self.ax2.bar(
            [0], [self.parameters.turret.min_firing_interval], color="green"
        )

        self.set_subplot_titles()
        self.set_board_boundaries()
        self.set_charging_time()

    @property
    def plots(self):
        return [
            self.obstacles,
            self.rocket_body,
            self.engine_bridge,
            self.main_engine_thrust,
            self.left_front_thrust,
            self.left_rear_thrust,
            self.right_front_thrust,
            self.right_rear_thrust,
            self.turret_body,
            self.turret_barrel,
            self.projectiles,
            self.charging,
        ]

    @ property
    def result(self):

        return self.title != self.parameters.animation.default_title

    def set_title(self):

        if self.result:
            return
        
        rocket_controller = self.controllers.rocket_controller
        turret_controller = self.controllers.turret_controller

        if rocket_controller.error or turret_controller.error:
            print(f"Rocket error: {rocket_controller.error}")
            print(f"Turret error: {turret_controller.error}")

            if rocket_controller.error and turret_controller.error:
                self.title = "DRAW: Both controllers failed simultaneously"
            elif rocket_controller.error:
                self.title = "TURRET WIN: Rocket controller failed"
            else:
                self.title = "ROCKET WIN: Turret controller failed"

            return

        if not rocket_controller.inputs_valid and not turret_controller.inputs_valid:
            self.title = "DRAW: Both sets of inputs are invalid"
        elif not rocket_controller.inputs_valid:
            self.title = "TURRET WIN: Rocket inputs invalid"
        elif not turret_controller.inputs_valid:
            self.title = "ROCKET WIN: Turret inputs invalid"


    def set_subplot_titles(self):

        self.ax.set_title("Game board")
        self.ax2.set_title("Ready to fire")

    def set_board_boundaries(self):

        width = self.parameters.environment.width
        height = self.parameters.environment.height

        self.ax.set(
            xlim=[-width / 2, width / 2], ylim=[-height / 2, height / 2], aspect=1
        )

    def set_charging_time(self):

        min_firing_interval = self.parameters.turret.min_firing_interval
        self.ax2.set_ylim(0, min_firing_interval)

        self.ax2.xaxis.set_visible(False)
        self.ax2.yaxis.tick_right()

    def plot_obstacles(self):

        x_values = [
            obstacle.location.x for obstacle in self.parameters.environment.obstacles
        ]
        y_values = [
            obstacle.location.y for obstacle in self.parameters.environment.obstacles
        ]
        return self.ax.scatter(x_values, y_values, c="y", marker="s")

    def plot_turret_body(self):

        location = self.parameters.turret.location
        return self.ax.scatter([location.x], [location.y], c="b")

    def plot_board(self):

        self.set_alpha()

        self.update_title()

        self.plot_charging()

        self.plot_rocket()
        self.plot_turret_barrel()
        self.plot_projectiles()

    def set_alpha(self):

        for p in self.plots:
            p.set_alpha(self.alpha)

    def update_title(self):

        current_time = self.history.time
        self.fig.suptitle(self.title + f" ({current_time:.1f}s)")

    def plot_charging(self):

        current_time = self.history.time
        last_fired = self.history.turret.last_fired
        min_firing_interval = self.parameters.turret.min_firing_interval

        charging_duration = (
            min(current_time - last_fired, min_firing_interval)
            if last_fired
            else min_firing_interval
        )

        self.charging.set_height(charging_duration)

        if math.isclose(charging_duration, min_firing_interval):
            self.charging.set_color("green")
        else:
            self.charging.set_color("red")

    def plot_rocket(self):

        self.plot_rocket_body()
        self.plot_engine_bridge()
        if self.history.rocket.main_engine_forces:  # Is there something to plot
            self.plot_main_engine_thrust()
            self.plot_left_front_thrust()
            self.plot_left_rear_thrust()
            self.plot_right_front_thrust()
            self.plot_right_rear_thrust()

    def plot_rocket_body(self):

        rocket_front_location, rocket_rear_location = self.get_rocket_ends()

        self.rocket_body.set_data(
            [rocket_front_location.x, rocket_rear_location.x],
            [rocket_front_location.y, rocket_rear_location.y],
        )

    def get_rocket_ends(self):

        rocket_location = self.history.rocket.location
        rocket_angle = self.history.rocket.angle
        rocket_length = self.parameters.rocket.length

        relative_rocket_end = PolarCoordinate(
            rocket_length / 2, rocket_angle
        ).pol2cart()

        rocket_front_location = rocket_location + relative_rocket_end
        rocket_rear_location = rocket_location - relative_rocket_end

        return rocket_front_location, rocket_rear_location

    def plot_engine_bridge(self):

        (
            engine_bridge_left_location,
            engine_bridge_right_location,
        ) = self.get_engine_bridge_ends()

        self.engine_bridge.set_data(
            [engine_bridge_left_location.x, engine_bridge_right_location.x],
            [engine_bridge_left_location.y, engine_bridge_right_location.y],
        )

    def get_engine_bridge_ends(self):

        _, rocket_rear_location = self.get_rocket_ends()

        rocket_length = self.parameters.rocket.length
        engine_bridge_width = (
            self.parameters.animation.rocket_length_engine_bridge_width_ratio
            * rocket_length
        )

        rocket_angle = self.history.rocket.angle

        perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
        relative_engine_end = PolarCoordinate(
            engine_bridge_width / 2, perpendicular_angle
        ).pol2cart()

        engine_bridge_left_location = rocket_rear_location + relative_engine_end
        engine_bridge_right_location = rocket_rear_location - relative_engine_end

        return engine_bridge_left_location, engine_bridge_right_location

    def plot_main_engine_thrust(self):

        force = self.history.rocket.main_engine_force
        _, projection_location = self.get_rocket_ends()
        relative_engine_angle = math.pi
        engine_plot = self.main_engine_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_left_front_thrust(self):

        force = self.history.rocket.left_front_thruster_force
        projection_location, _ = self.get_rocket_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_front_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_left_rear_thrust(self):

        force = self.history.rocket.left_rear_thruster_force
        projection_location, _ = self.get_engine_bridge_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_rear_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_right_front_thrust(self):

        force = self.history.rocket.right_front_thruster_force
        projection_location, _ = self.get_rocket_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_front_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_right_rear_thrust(self):

        force = self.history.rocket.right_rear_thruster_force
        _, projection_location = self.get_engine_bridge_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_rear_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    ):

        rocket_angle = self.history.rocket.angle
        projection_angle = normalise_angle(rocket_angle + relative_engine_angle)

        max_main_engine_force = self.parameters.rocket.max_main_engine_force
        rocket_length = self.parameters.rocket.length
        thrust_ratio = force / max_main_engine_force
        edge_length = (
            self.parameters.animation.rocket_length_max_thrust_length_ratio
            * rocket_length
            * thrust_ratio
        )

        left_angle = normalise_angle(
            projection_angle + self.parameters.animation.thrust_cone_angle
        )
        relative_thrust_left_location = PolarCoordinate(
            edge_length, left_angle
        ).pol2cart()
        thrust_left_location = projection_location + relative_thrust_left_location

        right_angle = normalise_angle(
            projection_angle - self.parameters.animation.thrust_cone_angle
        )
        relative_thrust_right_location = PolarCoordinate(
            edge_length, right_angle
        ).pol2cart()
        thrust_right_location = projection_location + relative_thrust_right_location

        engine_plot.set_data(
            [
                projection_location.x,
                thrust_left_location.x,
                thrust_right_location.x,
                projection_location.x,
            ],
            [
                projection_location.y,
                thrust_left_location.y,
                thrust_right_location.y,
                projection_location.y,
            ],
        )

    def plot_turret_barrel(self):

        barrel_length = (
            self.parameters.animation.square_root_board_area_barrel_length_ratio
            * math.sqrt(self.parameters.environment.board_area)
        )

        turret_location = self.parameters.turret.location
        turret_angle = self.history.turret.angle
        relative_barrel_tip_location = PolarCoordinate(
            barrel_length, turret_angle
        ).pol2cart()

        barrel_tip_location = turret_location + relative_barrel_tip_location

        self.turret_barrel.set_data(
            [turret_location.x, barrel_tip_location.x],
            [turret_location.y, barrel_tip_location.y],
        )

    def plot_projectiles(self):

        active_projectile_locations = [
            list(p.location) for p in self.history.projectiles if p.on_board
        ]

        # TODO: Cannot deal with cases where the number of projectiles on
        # the board drops to 0
        if active_projectile_locations:
            self.projectiles.set_offsets(active_projectile_locations)
