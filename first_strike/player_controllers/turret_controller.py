from typing import Tuple

from controller import Controller
from helpers import Helpers
from history import History
from parameters import Parameters
from physics import Physics


class TurretController(Controller):

    def calc_inputs(self) -> Tuple[float, bool]:

        raise NotImplementedError
