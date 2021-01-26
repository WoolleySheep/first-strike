import math

from coordinate_classes import Coordinate


def normalise_angle(angle: float) -> float:

    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi

    return angle


def distance_between_coordinates(coord1: Coordinate, coord2: Coordinate) -> float:

    return (coord1 - coord2).magnitude


def calc_minimum_distance_between(location1, velocity1, location2, velocity2):

    x1 = velocity2.x - velocity1.x
    x2 = location2.x - location1.x
    y1 = velocity2.y - velocity1.y
    y2 = location2.y - location1.y

    a = x1 ** 2 + y1 ** 2
    b = 2 * (x1 * x2 + y1 * y2)
    c = x2 ** 2 + y2 ** 2

    try:
        t_m = -b / (2 * a)  # Find time for local minima
        if t_m < 0:  # If the minimum occurs in the past, set min time to 0
            t_m = 0.0
    except ZeroDivisionError:  # When rocket and projectile have exactly equal velocity
        t_m = 0.0

    location1_at_tm = location1 + velocity1 * t_m
    location2_at_tm = location2 + velocity2 * t_m

    smallest_dist = distance_between_coordinates(location1_at_tm, location2_at_tm)

    return t_m, smallest_dist, (location1_at_tm, location2_at_tm)
