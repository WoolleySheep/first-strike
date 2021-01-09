import math

def normalise_angle(angle):

    while angle > math.pi: angle -= 2 * math.pi
    while angle <= -math.pi: angle += 2 * math.pi

    return angle