from copy import deepcopy
import time

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
        state_copy,
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
        self.parameters = parameters
        self.state_copy = state_copy
        self.error = None
        self.execution_time = None
        self.state_changed = None
        self.inputs = None
        self.inputs_valid = None

    @property
    def issue_raised(self):
        return (
            self.error
            or self.state_changed
            or not self.inputs_valid
            or self.execution_time_exceeded
        )

    def calc_inputs(self):

        catch_errors = True  # True for real games
        active_controller = "default"

        controller = (
            self.default_controller
            if active_controller == "default"
            else self.player_controller
        )

        start_time = time.time()
        try:
            self.inputs = controller.calc_inputs()
        except Exception as error:
            self.error = error
            if not catch_errors:
                raise
        self.execution_time = time.time() - start_time

    def are_inputs_valid(self):
        raise NotImplementedError

    def store_inputs(self):
        raise NotImplementedError

    @property
    def execution_time_exceeded(self):
        if self.execution_time is None:
            return None

        return self.execution_time > self.parameters.time.timestep

    def is_state_changed(self):

        self.state_changed = (
            self.state_copy[0] != self.parameters or self.state_copy[1] != self.history
        )

    def process_inputs(self):

        self.calc_inputs()
        if self.error or self.execution_time_exceeded:
            return

        self.is_state_changed()
        if not self.state_changed:
            self.are_inputs_valid()


class RocketMetaController(MetaController):
    def __init__(self, parameters, history, physics, helpers, state_copy):
        super().__init__(
            parameters,
            history,
            physics,
            helpers,
            state_copy,
            DefaultRocketController,
            PlayerRocketController,
        )

    def are_inputs_valid(self):

        self.inputs_valid = (
            len(self.inputs) == 5
            and all((type(input_) is float for input_ in self.inputs))
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
    def __init__(self, parameters, history, physics, helpers, state_copy):
        super().__init__(
            parameters,
            history,
            physics,
            helpers,
            state_copy,
            DefaultTurretController,
            PlayerTurretController,
        )

    def are_inputs_valid(self):

        max_rotation_speed = self.parameters.turret.max_rotation_speed
        self.inputs_valid = (
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
        self.parameters = parameters
        self.history = history
        self.state_copy = [None, None]
        self.rocket_controller = RocketMetaController(
            parameters, history, physics, helpers, self.state_copy
        )
        self.turret_controller = TurretMetaController(
            parameters, history, physics, helpers, self.state_copy
        )

    @property
    def issue_raised(self):
        return (
            self.rocket_controller.issue_raised or self.turret_controller.issue_raised
        )

    def store_state_copy(self):

        self.state_copy[0] = deepcopy(self.parameters)
        self.state_copy[1] = deepcopy(self.history)

    def process_inputs(self):

        self.store_state_copy()

        self.rocket_controller.process_inputs()
        if self.rocket_controller.state_changed:
            return

        self.turret_controller.process_inputs()

        if not self.issue_raised:
            self.rocket_controller.store_inputs()
            self.turret_controller.store_inputs()
