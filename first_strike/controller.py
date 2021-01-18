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

    def are_inputs_valid(self):
        raise NotImplemented

class RocketMetaController(MetaController):

    def __init__(self, parameters, history, helpers, physics):
        super().__init__(parameters, history, helpers, physics, DefaultRocketController, PlayerRocketController)

    def are_inputs_valid(self):

        return len(rocket_inputs) == 5
        and all([type(input_) is float for input_ in rocket_inputs])
        and 0 <= rocket_inputs[0] <= self.parameters.rocket.max_main_engine_force
        and all(
            [
                0 <= input_ <= self.parameters.rocket.max_thruster_force
                for input_ in rocket_inputs[1:]
            ]
        )


class TurretMetaController(MetaController):

    def __init__(self, parameters, history, helpers, physics):
        super().__init__(parameters, history, helpers, physics, DefaultTurretController, PlayerTurretController)

    def are_inputs_valid(self):

        max_rotation_speed = self.parameters.turret.max_rotation_speed
        return (
            len(turret_inputs) == 2
            and type(turret_inputs[0]) is float
            and -max_rotation_speed <= turret_inputs[0] <= max_rotation_speed
            and type(turret_inputs[1]) is bool
            and (not turret_inputs[1] or self.helpers.can_turret_fire())
        )

class Controllers():

    def __init__(self, parameters, history, helpers, physics):
        self.rocket_controller = RocketMetaController(parameters, history, helpers, physics)
        self.turret_controller = TurretMetaController(parameters, history, helpers, physics)

