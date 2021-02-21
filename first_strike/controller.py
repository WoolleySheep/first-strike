from abc import ABC, abstractmethod

from controller_helpers import ControllerHelpers
from helpers import Helpers
from history import History
from parameters import Parameters
from physics import Physics


class Controller(ABC):
    def __init__(
        self,
        parameters: Parameters,
        history: History,
        physics: Physics,
        helpers: Helpers,
    ):
        self.parameters = parameters
        self.history = history
        self.physics = physics
        self.helpers = helpers
        self.controller_helpers = ControllerHelpers(
            parameters, history, physics, helpers
        )

    @abstractmethod
    def calc_inputs(self):
        pass
