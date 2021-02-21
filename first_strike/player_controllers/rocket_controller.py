from typing import Tuple

from controller import Controller
from helpers import Helpers
from history import History
from parameters import Parameters
from physics import Physics


class RocketController(Controller):
    """Player controller for generating rocket inputs.

    The calculated inputs must be returned from the calc_inputs method.
    """

    def __init__(
        self,
        parameters: Parameters,
        history: History,
        physics: Physics,
        helpers: Helpers,
    ):
        super().__init__(parameters, history, physics, helpers)

    def calc_inputs(self) -> Tuple[float, float, float, float, float]:

        raise NotImplementedError
