from game_classes import Parameters, History
from helpers import Helpers
from physics import Physics
from default_controllers.rocket_controller import RocketController as DefaultRocketController
from default_controllers.turret_controller import TurretController as DefaultTurretController
from player_controllers.rocket_controller import RocketController as PlayerRocketController
from player_controllers.turret_controller import TurretController as PlayerTurretController

from dataclasses import dataclass

@dataclass
class Controller:
    parameters: Parameters
    history: History
    helpers: Helpers
    physics: Physics

    def calc_inputs(self):
        raise NotImplemented

class MetaController:



    def __init__(parameters, history, helpers, physics, default_controller, player_controller):
        self.default_controller = default_controller(parameters, history, helpers, physics)
        self.player_controller = player_controller(parameters, history, helpers, physics)

    def calc_inputs(self):
        
        player_inputs = self.player_controller.calc_inputs()
        if player_inputs:
            return player_inputs

        return self.default_controller.calc_inputs()

class RocketMetaController(MetaController):

    def __init__(self, parameters, history, helpers, physics):
        super().__init__(parameters, history, helpers, physics, DefaultRocketController, PlayerRocketController)

class TurretMetaController(MetaController):

    def __init__(self, parameters, history, helpers, physics):
        super().__init__(parameters, history, helpers, physics, DefaultTurretController, PlayerTurretController)

