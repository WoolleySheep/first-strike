import math

from math_helpers import normalise_angle

# Must be imported
from game_setup import game_data


def rocket_controller():

    max_thruster_force = game_data.properties.rocket_properties.max_thruster_force
    max_main_engine_force = game_data.properties.rocket_properties.max_main_engine_force

    # If facing away from the turret, spin the rocket using the thrusters
    # Use PID controller
    p_c = 0.5
    d_c = -0.7
    i_c = 0.01

    # Proportional
    angular_disp = angle_to_turret()

    # Integratal
    angles = game_data.history.rocket_history.angles
    timestep = game_data.environment.timestep
    integral_angles = sum(angles) * timestep

    # Derivative
    if len(angles) < 2:
        angular_vel = 0.0
    else:
        angular_vel = (angles[-1] - angles[-2]) / timestep

    control_signal = p_c * angular_disp + d_c * angular_vel + i_c * integral_angles

    thruster_force = min(abs(control_signal) * max_thruster_force, max_thruster_force)

    if control_signal > 0:
        lf, lr, rf, rr = 0.0, thruster_force, thruster_force, 0.0
    else:
        lf, lr, rf, rr = thruster_force, 0.0, 0.0, thruster_force

    # If turret is within cone of vision, turn on the main drive
    if abs(angular_disp) <= math.pi / 6:  # Cone of vision is hardcoded
        me = max_main_engine_force
    else:
        me = 0.0

    return me, lf, lr, rf, rr


def angle_to_turret():

    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]
    rocket_angle = game_data.history.rocket_history.angles[-1]
    turret_x, turret_y = game_data.properties.turret_properties.location

    angle = math.atan2(turret_y - rocket_y, turret_x - rocket_x)
    return normalise_angle(angle - rocket_angle)
