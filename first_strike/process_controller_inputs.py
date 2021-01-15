from rocket_controller import rocket_controller
from turret_controller import turret_controller
from game_helpers import has_sufficient_time_elapsed_since_last_shot


def process_controller_inputs(self):

    rocket_inputs, turret_inputs = _get_controller_inputs(self)

    if self.result:
        return

    _validate_inputs(self, rocket_inputs, turret_inputs)

    if self.result:
        return

    _record_controller_inputs(self, rocket_inputs, turret_inputs)


def _get_controller_inputs(self):

    rocket_controller_failed = False
    turret_controller_failed = False
    rocket_inputs = None
    turret_inputs = None
    rocket_error = None
    turret_error = None

    try:
        rocket_inputs = rocket_controller(self)
    except Exception as error:
        rocket_error = error
        rocket_controller_failed = True

    # try:
    turret_inputs = turret_controller(self)
    # except Exception as error:
    #     turret_error = error
    #     turret_controller_failed = True

    _check_controller_failure(
        self,
        rocket_controller_failed,
        rocket_error,
        turret_controller_failed,
        turret_error,
    )

    return (
        rocket_inputs,
        turret_inputs,
    )


def _check_controller_failure(
    self,
    rocket_controller_failed,
    rocket_error,
    turret_controller_failed,
    turret_error,
):

    if rocket_controller_failed and turret_controller_failed:
        self.title = "DRAW: Both controllers failed simultaneously"
    elif rocket_controller_failed:
        self.title = "TURRET WIN: Rocket controller failed"
    elif turret_controller_failed:
        self.title = "ROCKET WIN: Turret controller failed"

    if self.result:
        print(f"Rocket error: {rocket_error}")
        print(f"Turret error: {turret_error}")


def _validate_inputs(self, rocket_inputs, turret_inputs):

    rocket_inputs_invalid = (
        len(rocket_inputs) != 5
        or any([type(input_) is not float for input_ in rocket_inputs])
        or not (0 <= rocket_inputs[0] <= self.parameters.rocket.max_main_engine_force)
        or any(
            [
                not (0 <= input_ <= self.parameters.rocket.max_thruster_force)
                for input_ in rocket_inputs[1:]
            ]
        )
    )

    max_rotation_speed = self.parameters.turret.max_rotation_speed
    turret_inputs_invalid = (
        len(turret_inputs) != 2
        or type(turret_inputs[0]) is not float
        or not (-max_rotation_speed <= turret_inputs[0] <= max_rotation_speed)
        or type(turret_inputs[1]) is not bool
        or (turret_inputs[1] and not has_sufficient_time_elapsed_since_last_shot(self))
    )

    if rocket_inputs_invalid and turret_inputs_invalid:
        self.title = "DRAW: Both sets of inputs are invalid"
    elif rocket_inputs_invalid:
        self.title = "TURRET WIN: Rocket inputs invalid"
    elif turret_inputs_invalid:
        self.title = "ROCKET WIN: Turret inputs invalid"


def _record_controller_inputs(self, rocket_inputs, turret_inputs):

    (
        main_engine_force,
        lf_thruster_force,
        lr_thruster_force,
        rf_thruster_force,
        rr_thruster_force,
    ) = rocket_inputs
    rotation_velocity, fired = turret_inputs

    self.history.rocket.main_engine_forces.append(main_engine_force)
    self.history.rocket.left_front_thruster_forces.append(lf_thruster_force)
    self.history.rocket.left_rear_thruster_forces.append(lr_thruster_force)
    self.history.rocket.right_front_thruster_forces.append(rf_thruster_force)
    self.history.rocket.right_rear_thruster_forces.append(rr_thruster_force)

    self.history.turret.rotation_velocities.append(rotation_velocity)
    if fired:
        self.history.turret.when_fired.append(self.history.timesteps[-1])
