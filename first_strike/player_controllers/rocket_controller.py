from typing import Tuple

from controller import Controller
from history import History
from parameters import Parameters


class RocketController(Controller):
    """Player controller for generating rocket inputs.

    The calculated inputs must be returned from the calc_inputs method.
    """

    def calc_inputs(self) -> Tuple[float, float, float, float, float]:

        raise NotImplementedError
