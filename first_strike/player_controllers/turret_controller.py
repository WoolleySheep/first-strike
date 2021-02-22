from typing import Tuple

from controller import Controller
from helpers import Helpers
from history import History
from parameters import Parameters
from physics import Physics


class TurretController(Controller):
    def __init__(self, parameters, history):
        super().__init__(parameters, history)

    def calc_inputs(self) -> Tuple[float, bool]:

        raise NotImplementedError
