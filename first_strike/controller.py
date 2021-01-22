from game_classes import Parameters, History
from helpers import Helpers
from physics import Physics

from dataclasses import dataclass


@dataclass
class Controller:
    parameters: Parameters
    history: History
    physics: Physics
    helpers: Helpers

    def calc_inputs(self):
        raise NotImplementedError


