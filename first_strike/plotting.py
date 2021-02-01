import math
import matplotlib.pyplot as plt
import matplotlib.collections as collections

from math_helpers import normalise_angle, PolarCoordinate


class Plotting:
    def __init__(self, visual, parameters, history, helpers, controllers):
        self.visual = visual
        self.parameters = parameters
        self.history = history
        self.helpers = helpers
        self.controllers = controllers
        self.title = visual.default_title
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
            [0], [self.parameters.turret.min_firing_interval], color=self.visual.ready2fire_colour
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
    def result(self):

        return self.title != self.visual.default_title

    @property
    def alpha(self):

        return self.visual.game_over_alpha if self.result else 1.0

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
            plt.Circle((o.location.x, o.location.y), radius=o.radius, color=self.visual.obstacle_colour)
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

        if self.result:
            self.set_alpha()

        self.update_title()

        self.plot_charging()

        self.plot_rocket()
        self.plot_turret_barrel()
        self.plot_projectiles()

    def set_alpha(self):
        # TODO: Currently not changing the alpha of the obstacle patches

        for p in self.plots + self.ax.collections:
            p.set_alpha(self.alpha)

    def update_title(self):

        if self.result:
            self._set_title()
            return

        rocket_controller = self.controllers.rocket_controller
        turret_controller = self.controllers.turret_controller

        self.print_logs_if_controller_issue_raised()

        self.update_title_if_controller_issue_raised()

        self._set_title()

    def _set_title(self):

        current_time = self.history.time
        self.fig.suptitle(self.title + f" ({current_time:.1f}s)")

    def print_logs_if_controller_issue_raised(self):

        rocket_controller = self.controllers.rocket_controller
        turret_controller = self.controllers.turret_controller

        if rocket_controller.state_changed or turret_controller.state_changed:
            print("Rocket tampering: ", rocket_controller.state_changed)
            print("Turret tampering: ", turret_controller.state_changed)
            if self.controllers.state_copy[0] != self.parameters:
                print("Game parameters modified")
                print("Before controller execution:")
                print(self.controllers.state_copy[0])
                print("After controller execution:")
                print(self.parameters)

            if self.controllers.state_copy[1] != self.history:
                print("Game history modified")
                print("Before controller execution:")
                print(self.controllers.state_copy[1])
                print("After controller execution:")
                print(self.history)

        if rocket_controller.error or turret_controller.error:
            print(f"Rocket error: {rocket_controller.error}")
            print(f"Turret error: {turret_controller.error}")

        if (
            rocket_controller.inputs_valid is False
            or turret_controller.inputs_valid is False
        ):
            # Don't want to log if an input_valid is None
            print("Rocket inputs")
            print(f"    Valid: {rocket_controller.inputs_valid}")
            print(f"    Values: {rocket_controller.inputs}")
            print("Turret inputs")
            print(f"    Valid: {turret_controller.inputs_valid}")
            print(f"    Values: {turret_controller.inputs}")

        if (
            rocket_controller.execution_time_exceeded
            or turret_controller.execution_time_exceeded
        ):
            print(f"Rocket execution time: {rocket_controller.execution_time} sec")
            print(f"Turret execution time: {turret_controller.execution_time} sec")

    def update_title_if_controller_issue_raised(self):

        self._title_update_state_changed()

        if self.result:
            return

        self._title_update_error()

        if self.result:
            return

        self._title_update_execution_time_exceeded()

        if self.result:
            return

        self._title_update_inputs_invalid()

    def _title_update_inputs_invalid(self):

        if (
            not self.controllers.rocket_controller.inputs_valid
            and not self.controllers.turret_controller.inputs_valid
        ):
            self.title = "DRAW: Both sets of inputs are invalid"
        elif not self.controllers.rocket_controller.inputs_valid:
            self.title = "TURRET WIN: Rocket inputs invalid"
        elif not self.controllers.turret_controller.inputs_valid:
            self.title = "ROCKET WIN: Turret inputs invalid"

    def _title_update_execution_time_exceeded(self):

        if (
            self.controllers.rocket_controller.execution_time_exceeded
            and self.controllers.turret_controller.execution_time_exceeded
        ):
            self.title = "DRAW: Both controllers exceeded allowed execution time"
        elif self.controllers.rocket_controller.execution_time_exceeded:
            self.title = "TURRET WIN: Rocket controller exceeded allowed execution time"
        elif self.controllers.turret_controller.execution_time_exceeded:
            self.title = "ROCKET WIN: Turret controller exceeded allowed execution time"

    def _title_update_error(self):

        if (
            self.controllers.rocket_controller.error
            and self.controllers.turret_controller.error
        ):
            self.title = "DRAW: Both controllers failed simultaneously"
        elif self.controllers.rocket_controller.error:
            self.title = "TURRET WIN: Rocket controller failed"
        elif self.controllers.turret_controller.error:
            self.title = "ROCKET WIN: Turret controller failed"

    def _title_update_state_changed(self):

        if self.controllers.rocket_controller.state_changed:
            self.title = "TURRET WIN: Rocket controller tampered with the game"
        elif self.controllers.turret_controller.state_changed:
            self.title = "ROCKET WIN: Turret controller tampered with the game"

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
            self.visual.rocket_length_engine_bridge_width_ratio
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
            self.visual.rocket_length_max_thrust_length_ratio
            * rocket_length
            * thrust_ratio
        )

        left_angle = normalise_angle(
            projection_angle + self.visual.thrust_cone_angle
        )
        relative_thrust_left_location = PolarCoordinate(
            edge_length, left_angle
        ).pol2cart()
        thrust_left_location = projection_location + relative_thrust_left_location

        right_angle = normalise_angle(
            projection_angle - self.visual.thrust_cone_angle
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
            self.visual.barrel_length_turret_radius_ratio * self.parameters.turret.radius
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

        # TODO: Cannot deal with cases where the number of projectiles on
        # the board drops to 0
        if active_projectile_locations:
            self.projectiles.set_offsets(active_projectile_locations)

    def scale_object(self, radius: float):

        return 100 * radius ** 2 / self.parameters.environment.width
