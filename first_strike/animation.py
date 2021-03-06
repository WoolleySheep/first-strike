import matplotlib.animation as animation
import matplotlib.pyplot as plt
from history import History
from movement import Movement
from parameters import Parameters
from visual import Visual


class Animation:
    def __init__(
        self,
        visual: Visual,
        parameters: Parameters,
        history: History,
        controllers,
        plotting,
        result,
    ):
        self.visual = visual
        self.parameters = parameters
        self.history = history
        self.movement = Movement(parameters, history)
        self.controllers = controllers
        self.plotting = plotting
        self.result = result

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
            self.visual.frame_interval_ms / (1000 * self.parameters.time.timestep)
        )

    def update(self, _):

        for _ in range(self._ntimesteps_per_frame_refresh()):
            if not self.result.winner:
                self.controllers.process_inputs()
                self.result.check_controllers()
            if not self.result.winner:
                self.movement.move_objects()
                self.result.check_win_conditions()

        self.plotting.plot_board()

        return self.plotting.plots
