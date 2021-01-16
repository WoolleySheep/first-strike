import matplotlib.animation as animation
import matplotlib.pyplot as plt


from game_classes import Parameters, History


class Animation:
    def __init__(self, parameters: Parameters, history: History):
        self.parameters = parameters
        self.history = history
        self.title = parameters.animation.default_title
        self.fig, (self.ax, self.ax2) = plt.subplots(
            1, 2, gridspec_kw={"width_ratios": [5, 1]}
        )
        self.plots = Plots()
        self.animation_func = None

    from process_controller_inputs import process_controller_inputs
    from move_objects import move_objects
    from determine_winner import determine_winner
    from plot_board import plot_board

    def run(self):
        """Run the game"""

        self.animation_func = animation.FuncAnimation(
            self.fig,
            self.update,
            init_func=self.initialise,
            interval=self.parameters.animation.frame_interval_ms,
        )

        plt.show()

    @property
    def result(self):
        return self.title != self.parameters.animation.default_title

    @property
    def alpha(self):
        return self.parameters.animation.game_over_alpha if self.result else 1.0

    def initialise(self):

        self.set_subplot_titles()

        self.set_board_boundaries()

        self.set_charging_time()

        self.plots.obstacles = self.plot_obstacles()

        (self.plots.rocket_body,) = self.ax.plot([], c="g")
        (self.plots.engine_bridge,) = self.ax.plot([], c="g")
        (self.plots.main_engine_thrust,) = self.ax.plot([], c="r")
        (self.plots.left_front_thrust,) = self.ax.plot([], c="r")
        (self.plots.left_rear_thrust,) = self.ax.plot([], c="r")
        (self.plots.right_front_thrust,) = self.ax.plot([], c="r")
        (self.plots.right_rear_thrust,) = self.ax.plot([], c="r")

        self.plots.turret_body = self.plot_turret_body()
        (self.plots.turret_barrel,) = self.ax.plot([], c="b")

        self.plots.projectiles = self.ax.scatter([], [], c="k")

        (self.plots.charging,) = self.ax2.bar(
            [0], [self.parameters.turret.min_firing_interval], color="green"
        )

        return self.plots.all_plots

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

    def update(self, i):

        for _ in range(
            int(
                self.parameters.animation.frame_interval_ms
                / (1000 * self.parameters.time.timestep)
            )
        ):
            if not self.result:
                self.process_controller_inputs()
            if not self.result:
                self.move_objects()
                self.determine_winner()

        self.plot_board()

        return self.plots.all_plots


class Plots:
    def __init__(self):

        self.obstacles = None

        self.rocket_body = None
        self.engine_bridge = None
        self.main_engine_thrust = None
        self.left_front_thrust = None
        self.left_rear_thrust = None
        self.right_front_thrust = None
        self.right_rear_thrust = None

        self.turret_body = None
        self.turret_barrel = None

        self.projectiles = None

        self.charging = None

    @property
    def all_plots(self):

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
