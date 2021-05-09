import time
from abc import ABC, abstractmethod
from typing import Callable

from controller import Controller
from default_controllers.rocket_controller import (
    RocketController as DefaultRocketController,
)
from default_controllers.turret_controller import (
    TurretController as DefaultTurretController,
)
from math_helpers import float_in_range
from player_controllers.rocket_controller import (
    RocketController as PlayerRocketController,
)
from player_controllers.turret_controller import (
    TurretController as PlayerTurretController,
)


class MetaController(Controller, ABC):
    def __init__(
        self,
        parameters,
        history,
        state_copy,
        active_controller,
        raise_errors,
        check_execution_time,
        default_controller,
        player_controller,
    ):
        super().__init__(parameters, history)

        self.parameters = parameters
        self.state_copy = state_copy
        controller = (
            default_controller if active_controller == "default" else player_controller
        )
        self.controller = controller(parameters, history)
        self.raise_errors = raise_errors
        self.check_execution_time = check_execution_time
        self.error = None
        self.execution_time = None
        self.state_changed = None
        self.inputs = None
        self.inputs_valid = None

        if not self.raise_errors:
            self.calc_inputs = self._suppress_error_decorator(self.calc_inputs)
        if self.check_execution_time:
            self.calc_inputs = self._check_execution_time_decorator(self.calc_inputs)

    @property
    def issue_raised(self):
        return (
            self.error
            or self.state_changed
            or not self.inputs_valid
            or self.execution_time_exceeded
        )

    def _suppress_error_decorator(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                self.error = error

        return wrapper

    def _check_execution_time_decorator(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            self.execution_time = time.time() - start_time
            return result

        return wrapper

    def calc_inputs(self):  # pylint: disable=method-hidden

        self.inputs = self.controller.calc_inputs()

    @abstractmethod
    def are_inputs_valid(self):
        pass

    @abstractmethod
    def store_inputs(self):
        pass

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
    def __init__(
        self,
        parameters,
        history,
        state_copy,
        active_controller,
        raise_errors,
        check_execution_time,
    ):
        super().__init__(
            parameters,
            history,
            state_copy,
            active_controller,
            raise_errors,
            check_execution_time,
            DefaultRocketController,
            PlayerRocketController,
        )

    def are_inputs_valid(self):

        self.inputs_valid = (
            len(self.inputs) == 5
            and all(type(input_) is float for input_ in self.inputs)
            and float_in_range(
                self.inputs[0], 0, self.parameters.rocket.max_main_engine_force
            )
            and all(
                float_in_range(input_, 0, self.parameters.rocket.max_thruster_force)
                for input_ in self.inputs[1:]
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
    def __init__(
        self,
        parameters,
        history,
        state_copy,
        active_controller,
        raise_errors,
        check_execution_time,
    ):
        super().__init__(
            parameters,
            history,
            state_copy,
            active_controller,
            raise_errors,
            check_execution_time,
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
