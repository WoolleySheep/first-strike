from controller_helpers import ControllerHelpers
from game_classes import Parameters, History
from helpers import Helpers
from physics import Physics


class Controller:
    def __init__(self, parameters: Parameters, history: History, physics: Physics, helpers: Helpers):
        self.parameters = parameters
        self.history = history
        self.physics = physics
        self.helpers = helpers
        self.controller_helpers = ControllerHelpers(
            parameters, history, physics, helpers
        )

    def calc_inputs(self):
        raise NotImplementedError
