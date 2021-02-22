from copy import deepcopy

from meta_controller import RocketMetaController, TurretMetaController


class Controllers:
    def __init__(self, parameters, history, controller_parameters):
        self.parameters = parameters
        self.history = history
        self.state_copy = [None, None]
        (
            rocket_active_controller,
            turret_active_controller,
            rocket_raise_errors,
            turret_raise_errors,
            rocket_check_execution_time,
            turret_check_execution_time,
        ) = controller_parameters
        self.rocket_controller = RocketMetaController(
            parameters,
            history,
            self.state_copy,
            rocket_active_controller,
            rocket_raise_errors,
            rocket_check_execution_time,
        )
        self.turret_controller = TurretMetaController(
            parameters,
            history,
            self.state_copy,
            turret_active_controller,
            turret_raise_errors,
            turret_check_execution_time,
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
