import math

from helpers import normalise_angle

# Must be imported
from game_setup import game_data

def rocket_controller():

    thruster_force = game_data.properties.rocket_properties.thruster_force
    main_engine_force = game_data.properties.rocket_properties.main_engine_force

    # If facing away from the turret, spin the rocket using the thrusters
    angle_turret_rel_to_rocket = angle_to_turret()
    if angle_turret_rel_to_rocket > 0:
        lf, lr, rf, rr = 0.0, thruster_force, thruster_force, 0.0
    else:
        lf, lr, rf, rr = thruster_force, 0.0, 0.0, thruster_force

    # If turret is within cone of vision, turn on the main drive
    if abs(angle_turret_rel_to_rocket) <= math.pi / 6:  # Cone of vision is hardcoded
        me = main_engine_force
    else:
        me = 0.0
    

    return me, lf, lr, rf, rr

def angle_to_turret():

    rocket_x, rocket_y = game_data.history.rocket_history.locations[-1]
    rocket_angle = game_data.history.rocket_history.angles[-1]
    turret_x, turret_y = game_data.properties.turret_properties.location

    angle = math.atan2(turret_y - rocket_y, turret_x - rocket_x)
    return normalise_angle(angle - rocket_angle)



