import math

from coordinate_classes import PolarCoordinate
from math_helpers import normalise_angle


def plot_board(self):

    set_alpha(self)

    update_title(self)

    plot_charging(self)

    plot_rocket(self)
    plot_turret(self)
    plot_projectiles(self)


def set_alpha(self):

    for p in self.plots.all_plots:
        if p != self.plots.charging:
            p.set_alpha(self.alpha)

    self.plots.charging.set_alpha(self.alpha)


def update_title(self):

    current_time = self.history.time
    self.fig.suptitle(self.title + f" ({current_time:.1f}s)")

def plot_charging(self):

    current_time = self.history.time
    last_fired = self.history.turret.last_fired
    min_firing_interval = self.parameters.turret.min_firing_interval

    charging_duration = min(current_time - last_fired, min_firing_interval) if last_fired else min_firing_interval

    self.plots.charging.set_height(charging_duration)  

    if math.isclose(charging_duration, min_firing_interval):
        self.plots.charging.set_color("green")  
    else:
        self.plots.charging.set_color("red")


def plot_rocket(self):

    plot_rocket_body(self)
    plot_engine_bridge(self)
    if self.history.rocket.main_engine_forces:  # Is there something to plot
        plot_main_engine_thrust(self)
        plot_left_front_thrust(self)
        plot_left_rear_thrust(self)
        plot_right_front_thrust(self)
        plot_right_rear_thrust(self)


def plot_rocket_body(self):

    rocket_front_location, rocket_rear_location = get_rocket_ends(self)

    self.plots.rocket_body.set_data(
        [rocket_front_location.x, rocket_rear_location.x],
        [rocket_front_location.y, rocket_rear_location.y],
    )


def get_rocket_ends(self):

    rocket_location = self.history.rocket.location
    rocket_angle = self.history.rocket.angle
    rocket_length = self.parameters.rocket.length

    relative_rocket_end = PolarCoordinate(rocket_length / 2, rocket_angle).pol2cart()

    rocket_front_location = rocket_location + relative_rocket_end
    rocket_rear_location = rocket_location - relative_rocket_end

    return rocket_front_location, rocket_rear_location


def plot_engine_bridge(self):

    (
        engine_bridge_left_location,
        engine_bridge_right_location,
    ) = get_engine_bridge_ends(self)

    self.plots.engine_bridge.set_data(
        [engine_bridge_left_location.x, engine_bridge_right_location.x],
        [engine_bridge_left_location.y, engine_bridge_right_location.y],
    )


def get_engine_bridge_ends(self):

    _, rocket_rear_location = get_rocket_ends(self)

    rocket_length = self.parameters.rocket.length
    engine_bridge_width = (
        self.parameters.animation.rocket_length_engine_bridge_width_ratio
        * rocket_length
    )

    rocket_angle = self.history.rocket.angle

    perpendicular_angle = normalise_angle(rocket_angle + math.pi / 2)
    relative_engine_end = PolarCoordinate(
        engine_bridge_width / 2, perpendicular_angle
    ).pol2cart()

    engine_bridge_left_location = rocket_rear_location + relative_engine_end
    engine_bridge_right_location = rocket_rear_location - relative_engine_end

    return engine_bridge_left_location, engine_bridge_right_location


def plot_main_engine_thrust(self):

    force = self.history.rocket.main_engine_force
    _, projection_location = get_rocket_ends(self)
    relative_engine_angle = math.pi
    engine_plot = self.plots.main_engine_thrust

    _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    )


def plot_left_front_thrust(self):

    force = self.history.rocket.left_front_thruster_force
    projection_location, _ = get_rocket_ends(self)
    relative_engine_angle = math.pi / 2
    engine_plot = self.plots.left_front_thrust

    _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    )


def plot_left_rear_thrust(self):

    force = self.history.rocket.left_rear_thruster_force
    projection_location, _ = get_engine_bridge_ends(self)
    relative_engine_angle = math.pi / 2
    engine_plot = self.plots.left_rear_thrust

    _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    )


def plot_right_front_thrust(self):

    force = self.history.rocket.right_front_thruster_force
    projection_location, _ = get_rocket_ends(self)
    relative_engine_angle = -math.pi / 2
    engine_plot = self.plots.right_front_thrust

    _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    )


def plot_right_rear_thrust(self):

    force = self.history.rocket.right_rear_thruster_force
    _, projection_location = get_engine_bridge_ends(self)
    relative_engine_angle = -math.pi / 2
    engine_plot = self.plots.right_rear_thrust

    _plot_engine_thrust(
        self, force, projection_location, relative_engine_angle, engine_plot
    )


def _plot_engine_thrust(
    self, force, projection_location, relative_engine_angle, engine_plot
):

    rocket_angle = self.history.rocket.angle
    projection_angle = normalise_angle(rocket_angle + relative_engine_angle)

    max_main_engine_force = self.parameters.rocket.max_main_engine_force
    rocket_length = self.parameters.rocket.length
    thrust_ratio = force / max_main_engine_force
    edge_length = (
        self.parameters.animation.rocket_length_max_thrust_length_ratio
        * rocket_length
        * thrust_ratio
    )

    left_angle = normalise_angle(
        projection_angle + self.parameters.animation.thrust_cone_angle
    )
    relative_thrust_left_location = PolarCoordinate(edge_length, left_angle).pol2cart()
    thrust_left_location = projection_location + relative_thrust_left_location

    right_angle = normalise_angle(
        projection_angle - self.parameters.animation.thrust_cone_angle
    )
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


def plot_turret(self):

    plot_turret_barrel(self)


def plot_turret_barrel(self):

    barrel_length = (
        self.parameters.animation.square_root_board_area_barrel_length_ratio
        * math.sqrt(self.parameters.environment.board_area)
    )

    turret_location = self.parameters.turret.location
    turret_angle = self.history.turret.angle
    relative_barrel_tip_location = PolarCoordinate(
        barrel_length, turret_angle
    ).pol2cart()

    barrel_tip_location = turret_location + relative_barrel_tip_location

    self.plots.turret_barrel.set_data(
        [turret_location.x, barrel_tip_location.x],
        [turret_location.y, barrel_tip_location.y],
    )


def plot_projectiles(self):

    active_projectile_locations = [
        list(p.location) for p in self.history.projectiles if p.on_board
    ]

    # TODO: Cannot deal with cases where the number of projectiles on
    # the board drops to 0
    if active_projectile_locations:
        self.plots.projectiles.set_offsets(active_projectile_locations)
