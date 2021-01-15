import math

from coordinate_classes import Coordinate, PolarCoordinate
from math_helpers import normalise_angle, distance_between_coordinates
from rocket_physics import calc_rocket_angular_velocity

from player_controllers.player_rocket_controller import player_rocket_controller


def rocket_controller(self):

    player_controller_inputs = player_rocket_controller(self)
    if player_controller_inputs is not None:
        return player_controller_inputs

    return default_rocket_controller(self)


def default_rocket_controller(self):

    max_main_engine_force = self.parameters.rocket.max_main_engine_force
    max_thruster_force = self.parameters.rocket.max_thruster_force
    rocket_location = self.history.rocket.location
    turret_location = self.parameters.turret.location

    turret_attraction_factor = 5
    edge_avoidance_factor = 3
    projectile_avoidance_factor = 2


    # Position relative to turret
    dist2turret = distance_between_coordinates(rocket_location, turret_location)
    angle2turret = math.atan2(
        *list(self.parameters.turret.location - self.history.rocket.location)[::-1]
    )
    turret_attraction = PolarCoordinate(1 / dist2turret, angle2turret).pol2cart()

    # Board position
    width = self.parameters.environment.width
    height = self.parameters.environment.height

    edge_avoidance = Coordinate(1 / (height / 2 - rocket_location.y), 1 / (width / 2 - rocket_location.x))

    # Position relative to projectiles
    projectile_avoidance = Coordinate(0.0, 0.0)
    for projectile in self.history.projectiles:
        gradient = math.tan(projectile.firing_angle)
        y_value = gradient * (rocket_location.x - turret_location.x) + turret_location.y
        avoidance_angle = normalise_angle(projectile.firing_angle + (math.pi / 2) * [-1, 1][rocket_location.y > y_value])
        dist = distance_between_coordinates(rocket_location, projectile.location)
        projectile_avoidance += PolarCoordinate(1 / dist, avoidance_angle).pol2cart()

    direction = turret_attraction_factor * turret_attraction + edge_avoidance_factor * edge_avoidance + projectile_avoidance_factor * projectile_avoidance

    print("Turret: ", turret_attraction)
    print("Edge: ", edge_avoidance)
    print("Projectile: ", projectile_avoidance)
    print("Total: ", direction)


    # If facing away from the turret, spin the rocket using the thrusters
    # Use PID controller
    p_c = 1.0
    d_c = -0.7
    i_c = 0.01

    # Proportional
    angular_disp = angle_to_turret(self)

    # Integratal
    angles = self.history.rocket.angles
    timestep = self.parameters.time.timestep
    integral_angles = sum(angles) * timestep

    # Derivative
    angular_vel = calc_rocket_angular_velocity(self)

    control_signal = p_c * angular_disp + d_c * angular_vel + i_c * integral_angles

    thruster_force = min(abs(control_signal) * max_thruster_force, max_thruster_force)

    if control_signal > 0:
        lf, lr, rf, rr = 0.0, thruster_force, thruster_force, 0.0
    else:
        lf, lr, rf, rr = thruster_force, 0.0, 0.0, thruster_force

    # If turret is in front of the rocket, turn on the main engine
    # Increase engine power the better aligned the rocket is
    ratio = 1 - abs(angular_disp) / (math.pi / 2)
    me = ratio * max_main_engine_force if ratio > 0 else 0.0

    return me, lf, lr, rf, rr


def angle_to_turret(self):

    rocket_angle = self.history.rocket.angle

    angle = math.atan2(
        *list(self.parameters.turret.location - self.history.rocket.location)[::-1]
    )

    return normalise_angle(angle - rocket_angle)
