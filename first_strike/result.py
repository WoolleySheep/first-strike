from controllers import Controllers
from helpers import Helpers
from history import History
from parameters import Parameters

GAME_ONGOING = None

DRAW = 1
ROCKET_WIN = 2
TURRET_WIN = 3

ROCKET_ERROR = 1
TURRET_ERROR = 2
BOTH_ERROR = 3

ROCKET_TIME_EXCEEDED = 4
TURRET_TIME_EXCEEDED = 5
BOTH_TIME_EXCEEDED = 6

ROCKET_TAMPERED = 7
TURRET_TAMPERED = 8

ROCKET_INPUT_INVALID = 9
TURRET_INPUT_INVALID = 10
BOTH_INPUT_INVALID = 11

ROCKET_OUT_OF_BOUNDS = 12
ROCKET_HIT_OBSTACLE = 13
PROJECTILE_HIT_ROCKET = 14
ROCKET_HIT_TURRET = 15
BOTH_DESTROYED = 16
GAME_TIME_EXCEEDED = 17


class Result:
    def __init__(
        self,
        parameters: Parameters,
        history: History,
        controllers: Controllers,
    ):
        self.parameters = parameters
        self.history = history
        self.helpers = Helpers(parameters, history)
        self.controllers = controllers
        self.rocket_controller = controllers.rocket_controller
        self.turret_controller = controllers.turret_controller
        self.cause: int = None

    def is_game_over(self):
        return bool(self.cause)

    @property
    def winner(self):

        cause2winner = {
            GAME_ONGOING: GAME_ONGOING,
            ROCKET_ERROR: TURRET_WIN,
            TURRET_ERROR: ROCKET_WIN,
            BOTH_ERROR: DRAW,
            ROCKET_TIME_EXCEEDED: TURRET_WIN,
            TURRET_TIME_EXCEEDED: ROCKET_WIN,
            BOTH_TIME_EXCEEDED: DRAW,
            ROCKET_TAMPERED: TURRET_WIN,
            TURRET_TAMPERED: ROCKET_WIN,
            ROCKET_INPUT_INVALID: TURRET_WIN,
            TURRET_INPUT_INVALID: ROCKET_WIN,
            BOTH_INPUT_INVALID: DRAW,
            ROCKET_OUT_OF_BOUNDS: TURRET_WIN,
            ROCKET_HIT_OBSTACLE: TURRET_WIN,
            PROJECTILE_HIT_ROCKET: TURRET_WIN,
            ROCKET_HIT_TURRET: ROCKET_WIN,
            BOTH_DESTROYED: DRAW,
            GAME_TIME_EXCEEDED: DRAW,
        }
        return cause2winner[self.cause]

    def check_controllers(self):

        if not self.controllers.issue_raised:
            return

        self._check_state_change()

        if self.winner:
            return

        self._check_error()

        if self.winner:
            return

        self._check_execution_time_exceeded()

        if self.winner:
            return

        self._check_inputs_invalid()

    def _check_state_change(self):

        if self.rocket_controller.state_changed:
            self.cause = ROCKET_TAMPERED
        elif self.turret_controller.state_changed:
            self.cause = TURRET_TAMPERED
        else:
            return

        if self.controllers.state_copy[0] != self.parameters:
            print("Game parameters modified")
            print("Before controller execution:")
            print(self.controllers.state_copy[0])
            print("After controller execution:")
            print(self.parameters)

        if self.controllers.state_copy[1] != self.history:
            print("Game history modified")
            print("Before controller execution:")
            print(self.controllers.state_copy[1])
            print("After controller execution:")
            print(self.history)

    def _check_error(self):

        if self.rocket_controller.error and self.turret_controller.error:
            self.cause = BOTH_ERROR
            print(f"Rocket error: {self.rocket_controller.error}")
            print(f"Turret error: {self.turret_controller.error}")
        elif self.rocket_controller.error:
            self.cause = ROCKET_ERROR
            print(f"Rocket error: {self.rocket_controller.error}")
        elif self.turret_controller.error:
            self.cause = TURRET_ERROR
            print(f"Turret error: {self.turret_controller.error}")

    def _check_execution_time_exceeded(self):

        if (
            self.rocket_controller.execution_time_exceeded
            and self.turret_controller.execution_time_exceeded
        ):
            self.cause = BOTH_TIME_EXCEEDED
            print(f"Rocket execution time: {self.rocket_controller.execution_time} sec")
            print(f"Turret execution time: {self.turret_controller.execution_time} sec")
        elif self.rocket_controller.execution_time_exceeded:
            self.cause = ROCKET_TIME_EXCEEDED
            print(f"Rocket execution time: {self.rocket_controller.execution_time} sec")
        elif self.turret_controller.execution_time_exceeded:
            self.cause = TURRET_TIME_EXCEEDED
            print(f"Turret execution time: {self.turret_controller.execution_time} sec")

    def _check_inputs_invalid(self):

        if (
            not self.rocket_controller.inputs_valid
            and not self.turret_controller.inputs_valid
        ):
            self.cause = BOTH_INPUT_INVALID
            print(f"Rocket inputs: {self.rocket_controller.inputs}")
            print(f"Turret inputs: {self.turret_controller.inputs}")
        elif not self.rocket_controller.inputs_valid:
            self.cause = ROCKET_INPUT_INVALID
            print(f"Rocket inputs: {self.rocket_controller.inputs}")
        elif not self.turret_controller.inputs_valid:
            self.cause = TURRET_INPUT_INVALID
            print(f"Turret inputs: {self.turret_controller.inputs}")

    def check_win_conditions(self):

        rocket_hit_turret = self.helpers.does_rocket_impact_turret()
        projectile_hit_rocket = self.helpers.does_projectile_impact_rocket()

        if not self.helpers.is_rocket_within_bounds():
            self.cause = ROCKET_OUT_OF_BOUNDS
        elif self.helpers.has_rocket_hit_obstacle():
            self.cause = ROCKET_HIT_OBSTACLE
        elif rocket_hit_turret and projectile_hit_rocket:
            self.cause = BOTH_DESTROYED
        elif rocket_hit_turret:
            self.cause = ROCKET_HIT_TURRET
        elif projectile_hit_rocket:
            self.cause = PROJECTILE_HIT_ROCKET
        elif self.helpers.is_game_time_exceeded():
            self.cause = GAME_TIME_EXCEEDED
