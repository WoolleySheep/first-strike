import math
import matplotlib.pyplot as plt
import matplotlib.collections as collections

from math_helpers import normalise_angle, PolarCoordinate
from result import (
    DRAW,
    ROCKET_WIN,
    TURRET_WIN,
    ROCKET_ERROR,
    TURRET_ERROR,
    BOTH_ERROR,
    ROCKET_TIME_EXCEEDED,
    TURRET_TIME_EXCEEDED,
    BOTH_TIME_EXCEEDED,
    ROCKET_TAMPERED,
    TURRET_TAMPERED,
    ROCKET_INPUT_INVALID,
    TURRET_INPUT_INVALID,
    BOTH_INPUT_INVALID,
    ROCKET_OUT_OF_BOUNDS,
    ROCKET_HIT_OBSTACLE,
    PROJECTILE_HIT_ROCKET,
    ROCKET_HIT_TURRET,
    BOTH_DESTROYED,
    GAME_TIME_EXCEEDED,
)


class Plotting:
    def __init__(self, visual, parameters, history, helpers, controllers, result):
        self.visual = visual
        self.parameters = parameters
        self.history = history
        self.helpers = helpers
        self.controllers = controllers
        self.result = result
        self.title = visual.default_title
        self.plotted_result = False
        self.fig, (self.ax, self.ax2) = plt.subplots(
            1, 2, gridspec_kw={"width_ratios": [5, 1]}
        )

        self.plot_obstacles()

        (self.rocket_body,) = self.ax.plot([], c=self.visual.rocket_colour)
        (self.engine_bridge,) = self.ax.plot([], c=self.visual.rocket_colour)
        (self.main_engine_thrust,) = self.ax.plot([], c=self.visual.thrust_cone_colour)
        (self.left_front_thrust,) = self.ax.plot([], c=self.visual.thrust_cone_colour)
        (self.left_rear_thrust,) = self.ax.plot([], c=self.visual.thrust_cone_colour)
        (self.right_front_thrust,) = self.ax.plot([], c=self.visual.thrust_cone_colour)
        (self.right_rear_thrust,) = self.ax.plot([], c=self.visual.thrust_cone_colour)

        self.plot_turret_body()
        (self.turret_barrel,) = self.ax.plot([], c=self.visual.turret_colour)

        self.projectiles = self.ax.scatter([], [], c=self.visual.projectile_colour)

        (self.charging,) = self.ax2.bar(
            [0],
            [self.parameters.turret.min_firing_interval],
            color=self.visual.ready2fire_colour,
        )

        self.set_subplot_titles()
        self.set_board_boundaries()
        self.set_charging_time()

    @property
    def plots(self):
        return [
            self.rocket_body,
            self.engine_bridge,
            self.main_engine_thrust,
            self.left_front_thrust,
            self.left_rear_thrust,
            self.right_front_thrust,
            self.right_rear_thrust,
            self.turret_barrel,
            self.projectiles,
            self.charging,
        ]

    @property
    def alpha(self):

        return self.visual.game_over_alpha if self.result.is_game_over() else 1.0

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

        obstacle_patches = [
            plt.Circle(
                (o.location.x, o.location.y),
                radius=o.radius,
                color=self.visual.obstacle_colour,
            )
            for o in self.parameters.environment.obstacles
        ]
        self.ax.add_collection(
            collections.PatchCollection(obstacle_patches, match_original=True)
        )

    def plot_turret_body(self):

        location = self.parameters.turret.location
        radius = self.parameters.turret.radius

        turret_body_patch = plt.Circle(
            (location.x, location.y), radius=radius, color=self.visual.turret_colour
        )
        self.ax.add_collection(
            collections.PatchCollection([turret_body_patch], match_original=True)
        )

    def plot_board(self):

        self.plot_charging()

        self.plot_rocket()
        self.plot_turret_barrel()
        self.plot_projectiles()

        self.update_plot_title()

        if self.result.is_game_over():
            self.set_alpha()
            self.plotted_result = True

    def set_alpha(self):

        for p in self.plots + self.ax.collections:
            p.set_alpha(self.alpha)

    def update_plot_title(self):

        if self.result.is_game_over():
            self.update_title()

        self._set_title()

    def _set_title(self):

        current_time = self.history.time
        self.fig.suptitle(f"{self.title} ({current_time:.1f}s)")

    def update_title(self):

        winner2title = {
            DRAW: "DRAW",
            ROCKET_WIN: "ROCKET WIN",
            TURRET_WIN: "TURRET WIN",
        }
        cause2title = {
            ROCKET_ERROR: "Rocket controller failed",
            TURRET_ERROR: "Turret controller failed",
            BOTH_ERROR: "Both controllers failed simultaneously",
            ROCKET_TIME_EXCEEDED: "Rocket controller exceeded allowed execution time",
            TURRET_TIME_EXCEEDED: "Turret controller exceeded allowed execution time",
            BOTH_TIME_EXCEEDED: "Both controllers exceeded allowed execution time",
            ROCKET_TAMPERED: "Rocket controller tampered with the game",
            TURRET_TAMPERED: "Turret controller tampered with the game",
            ROCKET_INPUT_INVALID: "Rocket inputs invalid",
            TURRET_INPUT_INVALID: "Turret inputs invalid",
            BOTH_INPUT_INVALID: "Both sets of inputs are invalid",
            ROCKET_OUT_OF_BOUNDS: "Rocket has gone out-of-bounds",
            ROCKET_HIT_OBSTACLE: "Rocket has hit an obstacle",
            PROJECTILE_HIT_ROCKET: "Projectile has hit the rocket",
            ROCKET_HIT_TURRET: "Rocket has hit the turret",
            BOTH_DESTROYED: "Both the rocket and turret have been destroyed",
            GAME_TIME_EXCEEDED: "Game time exceeded",
        }

        self.title = (
            f"{winner2title[self.result.winner]}: {cause2title[self.result.cause]}"
        )

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
            self.charging.set_color(self.visual.ready2fire_colour)
        else:
            self.charging.set_color(self.visual.not_ready2fire_colour)

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
            self.visual.rocket_length_engine_bridge_width_ratio * rocket_length
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
            self.visual.rocket_length_max_thrust_length_ratio
            * rocket_length
            * thrust_ratio
        )

        left_angle = normalise_angle(projection_angle + self.visual.thrust_cone_angle)
        relative_thrust_left_location = PolarCoordinate(
            edge_length, left_angle
        ).pol2cart()
        thrust_left_location = projection_location + relative_thrust_left_location

        right_angle = normalise_angle(projection_angle - self.visual.thrust_cone_angle)
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
            self.visual.barrel_length_turret_radius_ratio
            * self.parameters.turret.radius
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
            list(location)
            for location in self.helpers.get_active_projectile_locations()
        ]

        self.projectiles.set_offsets(active_projectile_locations or [[None, None]])
