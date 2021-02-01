import matplotlib.animation as animation
import matplotlib.pyplot as plt

from game_classes import Parameters, History, Visual


class Animation:
    def __init__(
        self,
        visual: Visual,
        parameters: Parameters,
        history: History,
        movement,
        controllers,
        plotting,
        determine_winner,
    ):
        self.visual = visual
        self.parameters = parameters
        self.history = history
        self.movement = movement
        self.controllers = controllers
        self.plotting = plotting
        self.determine_winner = determine_winner
        self.animation_func = None

    def run(self):
        """Run the game"""

        self.animation_func = animation.FuncAnimation(
            self.plotting.fig,
            self.update,
            init_func=self.initialise,
            interval=self.visual.frame_interval_ms,
        )

        plt.show()

    def initialise(self):

        return self.plotting.plots

    def _ntimesteps_per_frame_refresh(self):

        return int(
            self.visual.frame_interval_ms
            / (1000 * self.parameters.time.timestep)
        )

    def update(self, i):

        for _ in range(self._ntimesteps_per_frame_refresh()):
            if not self.plotting.result:
                self.controllers.process_inputs()
            if not self.plotting.result and not self.controllers.issue_raised:
                self.movement.move_objects()
                self.determine_winner.check_win_conditions()

        self.plotting.plot_board()

        return self.plotting.plots
