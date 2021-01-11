import math
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from game_data import PolarCoordinate
from game_helpers import does_projectile_impact_rocket, does_rocket_impact_turret, is_game_time_exceeded, has_sufficient_time_elapsed_since_last_shot
from game_setup import game_data
from generate_board import get_rocket_ends
from math_helpers import normalise_angle
from play import advance_game_data, is_rocket_within_bounds

from rocket_controller import rocket_controller
from turret_controller import turret_controller

BOARD_AREA_TO_BARREL_LENGTH_RATIO = 0.05
ROCKET_LENGTH_ENGINE_BRIDGE_RATIO = 0.3
ROCKET_LENGTH_MAX_ENGINE_THRUST_RATIO = 1.0
THRUST_CONE_ANGLE = math.pi / 6
DEFAULT_TITLE = "Game in progress"
ENGINES = ("main", "left-front", "left-rear", "right-front", "right-rear")

def record_inputs(rocket_inputs, turret_inputs):

    (
        main_engine_force,
        lf_thruster_force,
        lr_thruster_force,
        rf_thruster_force,
        rr_thruster_force,
    ) = rocket_inputs
    rotation_velocity, fired = turret_inputs

    rocket_history = game_data.history.rocket_history
    rocket_history.main_engine_forces.append(main_engine_force)
    rocket_history.left_front_thruster_forces.append(lf_thruster_force)
    rocket_history.left_rear_thruster_forces.append(lr_thruster_force)
    rocket_history.right_front_thruster_forces.append(rf_thruster_force)
    rocket_history.right_rear_thruster_forces.append(rr_thruster_force)

    turret_history = game_data.history.turret_history
    turret_history.rotation_velocities.append(rotation_velocity)
    if fired:
        turret_history.when_fired.append(game_data.history.timesteps[-1])


def get_rocket_ends():

    rocket_location = game_data.history.rocket_history.locations[-1]

    rocket_angle = game_data.history.rocket_history.angles[-1]
    rocket_length = game_data.properties.rocket_properties.length

    relative_rocket_end = PolarCoordinate(rocket_length / 2, rocket_angle).pol2cart()

    rocket_front_location = rocket_location + relative_rocket_end
    rocket_rear_location = rocket_location - relative_rocket_end

    return rocket_front_location, rocket_rear_location


def get_engine_bridge_ends():

    _, rocket_rear_location = get_rocket_ends()

    rocket_length = game_data.properties.rocket_properties.length
    engine_bridge_width = ROCKET_LENGTH_ENGINE_BRIDGE_RATIO * rocket_length

    rocket_angle = game_data.history.rocket_history.angles[-1]

    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_engine_end = PolarCoordinate(
        engine_bridge_width / 2, perpendicular_angle
    ).pol2cart()

    engine_bridge_left_location = rocket_rear_location + relative_engine_end
    engine_bridge_right_location = rocket_rear_location - relative_engine_end

    return engine_bridge_left_location, engine_bridge_right_location





class AnimateGame:
    def __init__(self):
        self.title = DEFAULT_TITLE
        self.fig, self.ax = plt.subplots()
        self.animation = animation.FuncAnimation(
            self.fig, self.update, init_func=self.initialise, interval=int(game_data.environment.timestep * 1000)
        )

    @property
    def alpha(self):
        return 0.3 if self.result else 1.0

    @ property
    def result(self):
        return self.title != DEFAULT_TITLE
        

    def initialise(self):

        self.set_board_boundaries()

        (self.rocket_body,) = self.ax.plot([], c="g")
        (self.engine_bridge,) = self.ax.plot([], c="g")
        (self.main_engine_thrust,) = self.ax.plot([], c="r")
        (self.left_front_thrust,) = self.ax.plot([], c="r")
        (self.left_rear_thrust,) = self.ax.plot([], c="r")
        (self.right_front_thrust,) = self.ax.plot([], c="r")
        (self.right_rear_thrust,) = self.ax.plot([], c="r")

        self.turret_body = self.plot_turret_body()
        (self.turret_barrel,) = self.ax.plot([], c="b")

        self.projectiles = self.ax.scatter([], [], c="k")

        self.plots = [
            self.rocket_body,
            self.engine_bridge,
            self.main_engine_thrust,
            self.left_front_thrust,
            self.left_rear_thrust,
            self.right_front_thrust,
            self.right_rear_thrust,
            self.turret_body,
            self.turret_barrel,
            self.projectiles,
        ]

    def set_board_boundaries(self):
        
        width = game_data.environment.width
        height = game_data.environment.height

        self.ax.axis([-width / 2, width / 2, -height / 2, height / 2])
        plt.gca().set_aspect("equal", adjustable="box")




    def update(self, i):
        
        if not self.result:
            rocket_inputs, turret_inputs = self.get_inputs()        
        if not self.result:
            record_inputs(rocket_inputs, turret_inputs)
            advance_game_data()
            self.determine_winner()

        self.plot_board()

        return self.plots

    def plot_board(self):

        self.set_alpha()

        self.update_title()

        self.plot_rocket()
        self.plot_turret()
        self.plot_projectiles()

    def set_alpha(self):

        for p in self.plots:
            p.set_alpha(self.alpha)

    def update_title(self):
        
        current_time = game_data.history.timesteps[-1]
        self.ax.set_title(self.title + f" ({current_time:.1f}s)")

    def plot_rocket(self):

        self.plot_rocket_body()
        self.plot_engine_bridge()
        if game_data.history.rocket_history.main_engine_forces: # Is there something to plot
            self.plot_main_engine_thrust()
            self.plot_left_front_thrust()
            self.plot_left_rear_thrust()
            self.plot_right_front_thrust()
            self.plot_right_rear_thrust()

    def plot_rocket_body(self):

        rocket_front_location, rocket_rear_location = get_rocket_ends()

        self.rocket_body.set_data(
            [rocket_front_location.x, rocket_rear_location.x],
            [rocket_front_location.y, rocket_rear_location.y],
        )

    def plot_engine_bridge(self):

        (
            engine_bridge_left_location,
            engine_bridge_right_location,
        ) = get_engine_bridge_ends()

        self.engine_bridge.set_data(
            [engine_bridge_left_location.x, engine_bridge_right_location.x],
            [engine_bridge_left_location.y, engine_bridge_right_location.y],
        )

    def plot_turret(self):

        self.plot_turret_barrel()

    def plot_turret_body(self):

        turret_location = game_data.properties.turret_properties.location
        return self.ax.scatter([turret_location.x], [turret_location.y], c="b")

    def plot_turret_barrel(self):

        barrel_length = BOARD_AREA_TO_BARREL_LENGTH_RATIO * math.sqrt(
            game_data.environment.board_area
        )

        turret_location = game_data.properties.turret_properties.location
        turret_angle = game_data.history.turret_history.angles[-1]
        relative_barrel_tip_location = PolarCoordinate(
            barrel_length, turret_angle
        ).pol2cart()

        barrel_tip_location = turret_location + relative_barrel_tip_location

        self.turret_barrel.set_data(
            [turret_location.x, barrel_tip_location.x],
            [turret_location.y, barrel_tip_location.y],
        )

    def plot_projectiles(self):

        projectiles = game_data.history.projectile_histories
        active_projectile_locations = []
        for projectile in projectiles:
            if projectile.on_board:
                location = projectile.locations[-1]
                active_projectile_locations.append(list(location))

        # TODO: Cannot deal with cases where the number of projectiles on
        # the board drops to 0
        if active_projectile_locations:
            self.projectiles.set_offsets(active_projectile_locations)

    def plot_main_engine_thrust(self):

        force = game_data.history.rocket_history.main_engine_forces[-1]
        _, projection_location = get_rocket_ends()
        relative_engine_angle = math.pi
        engine_plot = self.main_engine_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_left_front_thrust(self):

        force = game_data.history.rocket_history.left_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_front_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_left_rear_thrust(self):

        force = game_data.history.rocket_history.left_rear_thruster_forces[-1]
        projection_location, _ = get_engine_bridge_ends()
        relative_engine_angle = math.pi / 2
        engine_plot = self.left_rear_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_right_front_thrust(self):

        force = game_data.history.rocket_history.right_front_thruster_forces[-1]
        projection_location, _ = get_rocket_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_front_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def plot_right_rear_thrust(self):

        force = game_data.history.rocket_history.right_rear_thruster_forces[-1]
        _, projection_location = get_engine_bridge_ends()
        relative_engine_angle = -math.pi / 2
        engine_plot = self.right_rear_thrust

        self._plot_engine_thrust(
            force, projection_location, relative_engine_angle, engine_plot
        )

    def _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    ):

        rocket_angle = game_data.history.rocket_history.angles[-1]
        projection_angle = normalise_angle(rocket_angle + relative_engine_angle)

        max_main_engine_force = (
            game_data.properties.rocket_properties.max_main_engine_force
        )
        rocket_length = game_data.properties.rocket_properties.length
        thrust_ratio = force / max_main_engine_force
        edge_length = (
            ROCKET_LENGTH_MAX_ENGINE_THRUST_RATIO * rocket_length * thrust_ratio
        )

        left_angle = normalise_angle(projection_angle + THRUST_CONE_ANGLE)
        relative_thrust_left_location = PolarCoordinate(
            edge_length, left_angle
        ).pol2cart()
        thrust_left_location = projection_location + relative_thrust_left_location

        right_angle = normalise_angle(projection_angle - THRUST_CONE_ANGLE)
        relative_thrust_right_location = PolarCoordinate(
            edge_length, right_angle
        ).pol2cart()
        thrust_right_location = projection_location + relative_thrust_right_location

        engine_plot.set_data(
            [
                projection_location.x,
                thrust_left_location.x,
                thrust_right_location.x,
                projection_location.x,
            ],
            [
                projection_location.y,
                thrust_left_location.y,
                thrust_right_location.y,
                projection_location.y,
            ],
        )

    def get_inputs(self):

        rocket_controller_failed = False
        turret_controller_failed = False
        rocket_inputs = None
        turret_inputs = None
        rocket_error = None
        turret_error = None

        try:
            rocket_inputs = rocket_controller()
        except Exception as error:
            rocket_error = error
            rocket_controller_failed = True

        try:
            turret_inputs = turret_controller()
        except Exception as error:
            turret_error = error
            turret_controller_failed = True

        self.check_controller_failure(
        rocket_controller_failed, rocket_error, turret_controller_failed, turret_error
    )

        return (
            rocket_inputs,
            turret_inputs,
        )

    def check_controller_failure(
        self, rocket_controller_failed, rocket_error, turret_controller_failed, turret_error
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


    def validate_inputs(self, rocket_inputs, turret_inputs):

        rocket_inputs_invalid = (
            len(rocket_inputs) != 5
            or any([type(input_) is not float for input_ in rocket_inputs])
            or not (
                0
                <= rocket_inputs[0]
                <= game_data.properties.rocket_properties.max_main_engine_force
            )
            or any(
                [
                    not (
                        0
                        <= input_
                        <= game_data.properties.rocket_properties.max_thruster_force
                    )
                    for input_ in rocket_inputs[1:]
                ]
            )
        )

        max_rotation_speed = game_data.properties.turret_properties.max_rotation_speed
        turret_inputs_invalid = (
            len(turret_inputs) != 2
            or type(turret_inputs[0]) is not float
            or not (-max_rotation_speed <= turret_inputs[0] <= max_rotation_speed)
            or type(turret_inputs[1]) is not bool
            or (turret_inputs[1] and not has_sufficient_time_elapsed_since_last_shot())
        )

        if rocket_inputs_invalid and turret_inputs_invalid:
            self.title = "DRAW: Both sets of inputs are invalid"
        elif rocket_inputs_invalid:
            print("TURRET WIN: Rocket inputs invalid")
        elif turret_inputs_invalid:
            print("ROCKET WIN: Turret inputs invalid")


    def determine_winner(self):

        rocket_hit_turret = does_rocket_impact_turret()
        projectile_hit_rocket = does_projectile_impact_rocket()

        if not is_rocket_within_bounds():
            self.title = "TURRET WIN: The rocket has gone out-of-bounds"
        elif rocket_hit_turret and projectile_hit_rocket:
            self.title = "DRAW: The rocket and turret have destroyed each other"
        elif rocket_hit_turret:
            self.title = "ROCKET_WIN: The rocket has hit the tower"
        elif projectile_hit_rocket:
            self.title = "TURRET WIN: A projectile has hit the rocket"
        elif is_game_time_exceeded():
            self.title = "DRAW: Game time exceeded"



game = AnimateGame()
plt.show()
