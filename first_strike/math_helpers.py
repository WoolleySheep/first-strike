import math

from game_data import Coordinate, PolarCoordinate


def normalise_angle(angle):

    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi

    return angle
