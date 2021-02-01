from dataclasses import dataclass
import math
from typing import List, Tuple, Union, Optional


def float_in_range(value: float, lower_bound: float, upper_bound: float) -> bool:

    return (
        (lower_bound <= value <= upper_bound)
        or math.isclose(value, lower_bound)
        or math.isclose(value, upper_bound)
    )


def normalise_angle(angle: float) -> float:

    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi

    return angle


def average(values):

    if not values:
        raise ValueError

    return sum(values) / len(values)


class Coordinate:
    def __init__(
        self,
        value1: Union[Union[List[float], Tuple[float]], float],
        value2: Optional[float] = None,
    ):
        if value2 is None and type(value1) in (list, tuple) and len(value1) == 2:
            self.x = value1[0]
            self.y = value1[1]
        else:
            self.x = value1
            self.y = value2

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    def cart2pol(self):
        r = self.magnitude
        theta = self.angle

        return PolarCoordinate(r, theta)

    def distance2(self, coord: "Coordinate") -> float:

        return (coord - self).magnitude

    def angle2(self, coord: "Coordinate") -> float:

        return (coord - self).angle

    def __add__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x + other.x, self.y + other.y)
        return Coordinate(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x - other.x, self.y - other.y)
        return Coordinate(self.x - other, self.y - other)

    def __mul__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x * other.x, self.y * other.y)
        return Coordinate(other * self.x, other * self.y)

    def __truediv__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x / other.x, self.y / other.y)
        return Coordinate(self.x / other, self.y / other)

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __dtruediv__(self, other):
        return self.__truediv__(other)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Only two elements in class")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class PolarCoordinate:
    r: float
    theta: float

    def pol2cart(self):
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)

        return Coordinate(x, y)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class RelativeObjects:
    def __init__(
        self,
        object_a_location,
        object_b_location,
        object_a_velocity=Coordinate(0.0, 0.0),
        object_b_velocity=Coordinate(0.0, 0.0),
    ):
        self.object_a_location = object_a_location
        self.object_b_location = object_b_location
        self.object_a_velocity = object_a_velocity
        self.object_b_velocity = object_b_velocity

    @property
    def distance(self):
        return self.object_b_location.distance2(self.object_b_location)

    @property
    def angle_a2b(self):
        return self.object_a_location.angle2(self.object_b_location)

    @property
    def angle_b2a(self):
        return self.object_b_location.angle2(self.object_a_location)

    def minimum_distance_between_objects(self):

        x1 = self.object_b_velocity.x - self.object_a_velocity.x
        x2 = self.object_b_location.x - self.object_a_location.x
        y1 = self.object_b_velocity.y - self.object_a_velocity.y
        y2 = self.object_b_location.y - self.object_a_location.y

        a = x1 ** 2 + y1 ** 2
        b = 2 * (x1 * x2 + y1 * y2)
        # c = x2 ** 2 + y2 ** 2  (Not required)

        try:
            time_min_dist = -b / (2 * a)  # Find time for local minima
        except ZeroDivisionError:  # When rocket and projectile have exactly equal velocity
            time_min_dist = 0.0  # Distance between will be same at all times
        else:
            if (
                time_min_dist < 0
            ):  # If the minimum occurs in the past, set min time to 0
                time_min_dist = 0.0

        location_a_min_dist = (
            self.object_a_location + self.object_a_velocity * time_min_dist
        )
        location_b_min_dist = (
            self.object_b_location + self.object_b_velocity * time_min_dist
        )

        min_dist = location_a_min_dist.distance2(location_b_min_dist)

        return min_dist, time_min_dist, (location_a_min_dist, location_b_min_dist)

    def distance_between_objects_first_occurs(self, distance: float):

        x1 = self.object_b_velocity.x - self.object_a_velocity.x
        x2 = self.object_b_location.x - self.object_a_location.x
        y1 = self.object_b_velocity.y - self.object_a_velocity.y
        y2 = self.object_b_location.y - self.object_a_location.y

        a = x1 ** 2 + y1 ** 2
        b = 2 * (x1 * x2 + y1 * y2)
        c = x2 ** 2 + y2 ** 2 - distance ** 2

        determinant = b ** 2 - 4 * a * c

        if determinant < 0:
            return None  # Distance is always greater

        t1_dist = (-b - math.sqrt(determinant)) / (2 * a)
        t2_dist = (-b + math.sqrt(determinant)) / (2 * a)

        t_dist = min(t1_dist, t2_dist)

        location_a_dist = self.object_a_location + self.object_a_velocity * t_dist
        location_b_dist = self.object_b_location + self.object_b_velocity * t_dist

        return t_dist, (location_a_dist, location_b_dist)


# print(normalise_angle(6.169999999999913))
