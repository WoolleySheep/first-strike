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
