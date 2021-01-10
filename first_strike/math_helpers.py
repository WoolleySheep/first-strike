import math

def normalise_angle(angle):

    while angle > math.pi: angle -= 2 * math.pi
    while angle <= -math.pi: angle += 2 * math.pi

    return angle

def cart2pol(x, y):

    r = calc_magnitude(x, y)
    theta = math.atan2(y, x)

    return r, theta


def pol2cart(r, theta):

    x = r * math.cos(theta)
    y = r * math.sin(theta)

    return x, y


def calc_magnitude(x, y):

    return math.sqrt(x ** 2 + y ** 2)