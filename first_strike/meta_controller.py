from controller import Controller
from math_helpers import float_in_range

from default_controllers.rocket_controller import (
    RocketController as DefaultRocketController,
)
from default_controllers.turret_controller import (
    TurretController as DefaultTurretController,
)
from player_controllers.rocket_controller import (
    RocketController as PlayerRocketController,
)
from player_controllers.turret_controller import (
    TurretController as PlayerTurretController,
)


class MetaController(Controller):
    def __init__(
        self,
        parameters,
        history,
        physics,
        helpers,
        default_controller,
        player_controller,
    ):
        super().__init__(parameters, history, physics, helpers)
        self.default_controller = default_controller(
            parameters, history, physics, helpers
        )
        self.player_controller = player_controller(
            parameters, history, physics, helpers
        )
        self.error = None
        self.inputs = None
        self.inputs_valid = None

    def calc_inputs(self):

        try:
            self.inputs = self.player_controller.calc_inputs()
        except NotImplementedError:
            # try:
            self.inputs = self.default_controller.calc_inputs()
            # except Exception as error:
            # self.error = error
        except Exception as error:
            self.error = error

    def are_inputs_valid(self):
        raise NotImplementedError

    def store_inputs(self):
        raise NotImplementedError

    def process_inputs(self):

        self.calc_inputs()

        if self.error:
            return

        self.inputs_valid = self.are_inputs_valid()
        if self.inputs_valid:
            self.store_inputs()


class RocketMetaController(MetaController):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(
            parameters,
            history,
            physics,
            helpers,
            DefaultRocketController,
            PlayerRocketController,
        )

    def are_inputs_valid(self):

        return (
            len(self.inputs) == 5
            and all([type(input_) is float for input_ in self.inputs])
            and float_in_range(
                self.inputs[0], 0, self.parameters.rocket.max_main_engine_force
            )
            and all(
                [
                    float_in_range(input_, 0, self.parameters.rocket.max_thruster_force)
                    for input_ in self.inputs[1:]
                ]
            )
        )

    def store_inputs(self):

        (
            main_engine_force,
            lf_thruster_force,
            lr_thruster_force,
            rf_thruster_force,
            rr_thruster_force,
        ) = self.inputs

        self.history.rocket.main_engine_forces.append(main_engine_force)
        self.history.rocket.left_front_thruster_forces.append(lf_thruster_force)
        self.history.rocket.left_rear_thruster_forces.append(lr_thruster_force)
        self.history.rocket.right_front_thruster_forces.append(rf_thruster_force)
        self.history.rocket.right_rear_thruster_forces.append(rr_thruster_force)


class TurretMetaController(MetaController):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(
            parameters,
            history,
            physics,
            helpers,
            DefaultTurretController,
            PlayerTurretController,
        )

    def are_inputs_valid(self):

        max_rotation_speed = self.parameters.turret.max_rotation_speed
        return (
            len(self.inputs) == 2
            and type(self.inputs[0]) is float
            and float_in_range(self.inputs[0], -max_rotation_speed, max_rotation_speed)
            and type(self.inputs[1]) is bool
            and (not self.inputs[1] or self.helpers.can_turret_fire())
        )

    def store_inputs(self):

        rotation_velocity, fired = self.inputs

        self.history.turret.rotation_velocities.append(rotation_velocity)
        if fired:
            self.history.turret.when_fired.append(self.history.time)


class Controllers:
    def __init__(self, parameters, history, physics, helpers):
        self.rocket_controller = RocketMetaController(
            parameters, history, physics, helpers
        )
        self.turret_controller = TurretMetaController(
            parameters, history, physics, helpers
        )

    @property
    def error_occured(self):
        return (
            self.rocket_controller.error
            or self.turret_controller.error
            or not self.rocket_controller.inputs_valid
            or not self.turret_controller.inputs_valid
        )

    def process_inputs(self):

        self.rocket_controller.process_inputs()
        self.turret_controller.process_inputs()
