import matplotlib.animation as animation
import matplotlib.pyplot as plt


from game_classes import Parameters, History
from plotting import Plotting


class Animation:
    def __init__(self, parameters: Parameters, history: History, movement, controllers):
        self.parameters = parameters
        self.history = history
        self.movement = movement
        self.controllers = controllers
        self.plotting = Plotting(parameters, history, controllers)
        self.animation_func = None

    def run(self):
        """Run the game"""

        self.animation_func = animation.FuncAnimation(
            self.plotting.fig,
            self.update,
            init_func=self.initialise,
            interval=self.parameters.animation.frame_interval_ms,
        )

        plt.show()

    @property
    def result(self):
        return self.plotting.title != self.parameters.animation.default_title

    @property
    def alpha(self):
        return self.parameters.animation.game_over_alpha if self.result else 1.0

    def initialise(self):

        return self.plotting.plots

    def _ntimesteps_per_frame_refresh(self):

        return int(
            self.parameters.animation.frame_interval_ms
            / (1000 * self.parameters.time.timestep)
        )

    def update(self, i):

        for _ in range(self._ntimesteps_per_frame_refresh()):
            if not self.result:
                self.controllers.process_inputs()
            if not self.result:
                self.movement.move_objects()
                self.determine_winner()

        self.plotting.plot_board()

        return self.plotting.plots
