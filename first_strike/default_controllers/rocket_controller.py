import math

from coordinate_classes import Coordinate, PolarCoordinate
from math_helpers import normalise_angle, distance_between_coordinates
from rocket_physics import calc_rocket_angular_velocity, calc_rocket_velocity

from player_controllers.player_rocket_controller import player_rocket_controller


def rocket_controller(self):

    player_controller_inputs = player_rocket_controller(self)
    if player_controller_inputs is not None:
        return player_controller_inputs

    return default_rocket_controller(self)


def default_rocket_controller(self):
    def edge_repulsion(position, boundary):
        # TODO: This will break if the rocket sits on the boundary
        return (1 if position < 0 else -1) / (boundary / 2 - abs(position))

    max_main_engine_force = self.parameters.rocket.max_main_engine_force
    max_thruster_force = self.parameters.rocket.max_thruster_force
    rocket_location = self.history.rocket.location
    rocket_radius = self.parameters.rocket.target_radius
    turret_location = self.parameters.turret.location
    turret_radius = self.parameters.turret.target_radius

    turret_attraction_factor = 30
    edge_avoidance_factor = 5
    obstacle_avoidance_factor = 5
    projectile_avoidance_factor = 7
    firing_path_avoidance_factor = 3

    # Position relative to turret
    dist2turret = distance_between_coordinates(rocket_location, turret_location)
    angle2turret = math.atan2(
        *list(self.parameters.turret.location - self.history.rocket.location)[::-1]
    )
    turret_attraction = PolarCoordinate(
        1 / (dist2turret - turret_radius), angle2turret
    ).pol2cart()

    # Board position
    width = self.parameters.environment.width
    height = self.parameters.environment.height

    edge_avoidance = Coordinate(
        edge_repulsion(rocket_location.x, width),
        edge_repulsion(rocket_location.y, height),
    )

    # Position relative to projectile paths
    projectile_avoidance = Coordinate(0.0, 0.0)
    for projectile in self.history.projectiles:
        gradient = math.tan(projectile.firing_angle)
        y_value = gradient * (rocket_location.x - turret_location.x) + turret_location.y
        avoidance_angle = normalise_angle(
            projectile.firing_angle
            + (math.pi / 2) * [-1, 1][rocket_location.y > y_value]
        )
        dist = distance_between_coordinates(rocket_location, projectile.location)
        projectile_avoidance += PolarCoordinate(
            1 / (dist - rocket_radius), avoidance_angle
        ).pol2cart()

    # Position relative to obstacles
    obstacle_avoidance = Coordinate(0.0, 0.0)
    for obstacle in self.parameters.environment.obstacles:
        delta = rocket_location - obstacle.location
        obstacle_avoidance += PolarCoordinate(
            1 / (delta.magnitude - obstacle.radius), delta.angle
        ).pol2cart()

    # Position relative to turret firing path
    turret_angle = self.history.turret.angle
    gradient = math.tan(turret_angle)
    y_value = gradient * (rocket_location.x - turret_location.x) + turret_location.y
    avoidance_angle = normalise_angle(
        turret_angle + (math.pi / 2) * [-1, 1][rocket_location.y > y_value]
    )
    dist = distance_between_coordinates(rocket_location, turret_location)
    firing_path_avoidance = PolarCoordinate(1 / dist, avoidance_angle).pol2cart()

    direction = (
        turret_attraction_factor * turret_attraction
        + edge_avoidance_factor * edge_avoidance
        + obstacle_avoidance_factor * obstacle_avoidance
        + projectile_avoidance_factor * projectile_avoidance
        + firing_path_avoidance_factor * firing_path_avoidance
    )

    # Current velocity
    rocket_velocity = calc_rocket_velocity(self)
    rocket_vel_angle = rocket_velocity.angle

    thrust_direction = (
        PolarCoordinate(1.0, direction.angle).pol2cart()
        - PolarCoordinate(1.0, rocket_vel_angle).pol2cart()
    )
    thrust_angle = thrust_direction.angle

    rocket_angle = self.history.rocket.angle
    relative_thrust_angle = normalise_angle(thrust_angle - rocket_angle)

    # If facing away from the turret, spin the rocket using the thrusters
    # Use PD controller
    p_c = 1.0
    d_c = -0.7

    # Derivative
    angular_vel = calc_rocket_angular_velocity(self)

    control_signal = p_c * relative_thrust_angle + d_c * angular_vel

    thruster_force = min(abs(control_signal) * max_thruster_force, max_thruster_force)

    clockwise_thrust = [0.0, thruster_force][control_signal < 0]
    anticlockwise_thrust = [0.0, thruster_force][control_signal >= 0]

    rotational_outputs = [
        0.0,
        clockwise_thrust,
        anticlockwise_thrust,
        anticlockwise_thrust,
        clockwise_thrust,
    ]

    if not (-math.pi / 2 <= relative_thrust_angle <= math.pi / 2):
        return rotational_outputs

    left_thrusters_active = relative_thrust_angle < 0
    right_thrusters_active = relative_thrust_angle >= 0
    thrusters_active = [left_thrusters_active] * 2 + [right_thrusters_active] * 2

    engine_thruster_ratio = abs(math.tan(relative_thrust_angle))

    try:
        engine_outputs = [max_main_engine_force] + [
            thrust / (2 * engine_thruster_ratio) for thrust in thrusters_active
        ]
    except ZeroDivisionError:  # Engine thruster ratio is 0; no need for lateral movement
        return [max_main_engine_force] + rotational_outputs[1:]

    max_outputs = [max_main_engine_force] + [max_thruster_force] * 4
    remaining_outputs = [
        max_thrust - rotational_thrust
        for max_thrust, rotational_thrust in zip(max_outputs, rotational_outputs)
    ]

    try:
        output_ratios = [
            output / remaining
            for output, remaining in zip(engine_outputs, remaining_outputs)
        ]
    except ZeroDivisionError:  # Remaining thrust is 0; cannot manouver directionally
        return rotational_outputs

    max_ratio = max(output_ratios)
    directional_outputs = [output / max_ratio for output in engine_outputs]

    return [
        rotation + direction
        for rotation, direction in zip(rotational_outputs, directional_outputs)
    ]


def angle_to_turret(self):

    rocket_angle = self.history.rocket.angle

    angle = math.atan2(
        *list(self.parameters.turret.location - self.history.rocket.location)[::-1]
    )

    return normalise_angle(angle - rocket_angle)
