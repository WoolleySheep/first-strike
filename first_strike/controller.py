from abc import ABC, abstractmethod

from controller_helpers import ControllerHelpers
from helpers import Helpers
from history import History
from parameters import Parameters
from physics import Physics


class Controller(ABC):
    """Abstract base class for all controllers.

    Takes the current and past state of the game and generate inputs to the rocket and turret.
    """

    def __init__(
        self,
        parameters: Parameters,
        history: History,
    ):
        self.parameters = parameters
        self.history = history
        self.physics = Physics(parameters, history)
        self.helpers = Helpers(parameters, history)
        self.controller_helpers = ControllerHelpers(
            parameters, history, self.physics, self.helpers
        )

    @abstractmethod
    def calc_inputs(self):
        pass
