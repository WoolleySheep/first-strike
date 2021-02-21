"""Maths-related functions and classes"""

from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple, Union

ObjectDistanceInfo = Tuple[float, Tuple["Coordinate", "Coordinate"]]


def float_in_range(value: float, lower: float, upper: float) -> bool:
    """Checks if a float is within a range.

    In addition to checking if lower < value < upper, checks if value is close to the end points;
    if so, returns True. This is to account for the vageries of floating point precision.

    args:
        value: The value to check.
        lower: The lower bound of the range.
        upper: The upper bound of the range.
    return:
        _: The value is in the range.
    """

    return (
        (lower <= value <= upper)
        or math.isclose(value, lower)
        or math.isclose(value, upper)
    )


def normalise_angle(angle: float) -> float:
    """Normalises the angle in the range (-pi, pi].

    args:
        angle (rad): The angle to normalise.
    return:
        angle (rad): The normalised angle.
    """

    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi

    return angle


def average(values: Sequence) -> object:
    """Average a sequence of objects.

    Relies on two pre-conditions:
        - The values can be summed together
        - An instance of value can be divided by an int
    If the array-like structure is empty, will raise a ValueError.

    args:
        values: The array-like structure to average.
    return:
        _: The average value.
    """

    if not values:
        raise ValueError

    return sum(values) / len(values)


class Coordinate:
    """
    Class defining an (x, y) coordinate.

    Can be instantiated using either a pair of floats, or a length 2 sequence of floats.
        - Coordinate(1, 2)
        - Coordinate([1, 2])
        - Coordinate((1, 2))
    Basic arithmetic (add, sub, mul, div) is possible in combination with scalars or other coordinates.
        - Scalars will affect both the x and y values
            - Eg: 5 * Coordinate(1, 2) == Coordinate(5, 10)
        - The x values of other coordinates will affect the x value, and same for the y value
            - Eg: Coordinate(1, 2) + Coordinate(5, 1) == Coordinate(6, 3)
    """

    def __init__(
        self,
        value1: Union[Sequence[float], float],
        value2: Optional[float] = None,
    ):
        if value2 is None:
            assert len(value1) == 2
            self.x = value1[0]
            self.y = value1[1]
        else:
            self.x = value1
            self.y = value2

    @property
    def magnitude(self) -> float:
        """Calculates the distance of the coordinate from (0, 0).

        return:
            distance: The distance of the coordinate from (0, 0).
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self) -> float:
        """Calculates the angle of the coordinate from (0, 0).

        return:
            angle (rad): The angle of the coordinate from (0, 0).
        """
        return math.atan2(self.y, self.x)

    def cart2pol(self) -> "PolarCoordinate":
        """Calulates the equivalent instance of PolarCoordinate.

        return:
            polar: The equivalent instance of PolarCoordinate.
        """
        r = self.magnitude
        theta = self.angle

        return PolarCoordinate(r, theta)

    def distance2(self, coord: "Coordinate") -> float:
        """Calculates the distance from the current coordinate to another.

        args:
            coord: The other coordinate.
        return:
            distance: The distance between the coordinates.
        """
        return (coord - self).magnitude

    def angle2(self, coord: "Coordinate") -> float:
        """Calculates the angle from the current coordinate to another.

        args:
            coord: The other coordinate
        return:
            distance: The angle from the current coordinate to the other.

        """
        return (coord - self).angle

    def rotate_by(self, angle: float) -> "Coordinate":

        p = self.cart2pol()
        p.theta += angle
        return p.pol2cart()

    def __add__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        return Coordinate(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        return Coordinate(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x * other.x, self.y * other.y)
        return Coordinate(other * self.x, other * self.y)

    def __truediv__(self, other):
        if isinstance(other, Coordinate):
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
    """
    Class defining an (r, theta) polar coordinate.

    Not fully implemented; effectively only used for easily converting back to euclidian coordinates.
    """

    r: float
    theta: float

    def pol2cart(self) -> "Coordinate":
        """Calulates the equivalent instance of Coordinate.

        return:
            euclidian: The equivalent instance of Coordinate.
        """
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)

        return Coordinate(x, y)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class RelativeObjects:
    """Class defining the relationship between two objects moving with constant velocities.

    Attributes:
        - object_a_location: The current location of object a.
        - object_b_location: The current location of object b.
        - object_a_velocity: The current velocity of object a.
        - object_b_velocity: The current velocity of object b.
    Methods:
        - locations: Calculates the locations of objects a and b at a given time.
        - distance: Calculates the distance between object a and b at a given time.
        - angle: Angle from object a to b at a given time.
        - minimum_distance_between_objects: Calculates when and where objects a and b are closest together.
        - times_objects_within_distance: Calculates the times and locations that objects a and b are a given distance apart.
        - time_objects_first_within_distance: Calculates when and where objects a and b are first a given distance apart.

    """

    def __init__(
        self,
        object_a_location: Coordinate,
        object_b_location: Coordinate,
        object_a_velocity: Coordinate = Coordinate(0.0, 0.0),
        object_b_velocity: Coordinate = Coordinate(0.0, 0.0),
    ):
        """Create an instance of RelativeObjects

        args:
            - object_a_location: The current location of object a.
            - object_b_location: The current location of object b.
            - object_a_velocity: The current velocity of object a.
            - object_b_velocity: The current velocity of object b.
        """
        self.object_a_location = object_a_location
        self.object_b_location = object_b_location
        self.object_a_velocity = object_a_velocity
        self.object_b_velocity = object_b_velocity

    def locations(self, time: float = 0.0) -> Tuple[Coordinate, Coordinate]:
        """Calculates the locations of objects a and b at a given time.

        Defaults to the current time
        args:
            time:
        return:
            locations: Locations of objects a and b at the given time.
        """
        location_a = self._location(
            self.object_a_location, self.object_a_velocity, time
        )
        location_b = self._location(
            self.object_b_location, self.object_b_velocity, time
        )

        return location_a, location_b

    def distance(self, time: float = 0.0) -> float:
        """Calculates the distance between object a and b at a given time.

        Defaults to the current time
        args:
            time:
        return:
            distance: Distance between objects a and b at the given time.
        """
        location_a, location_b = self.locations()
        return location_a.distance2(location_b)

    def angle(self, time: float = 0.0) -> float:
        """Angle from object a to b at a given time.

        Defaults to the current time
        args:
            time:
        return:
            distance: Angle from object a to b at the given time.
        """
        location_a, location_b = self.locations()
        return location_a.angle2(location_b)

    @staticmethod
    def _location(
        current_location: Coordinate, velocity: Coordinate, time: float
    ) -> Coordinate:
        """Calculates the location an object will be at a given time.

        args:
            current_location:
            velocity:
            time:
        return:
            location: The location of the object at the given time.
        """
        return current_location + velocity * time

    def minimum_distance_between_objects(
        self,
    ) -> Tuple[float, float, Tuple[Coordinate, Coordinate]]:
        """Calculates when and where objects a and b are closest together.

        Assumes that the velocity of objects a and b will remain constant.
        Does not allow negative times; if the time when closest together is t < 0,
        then t will be set = 0.

        results: Information about the time and locations of objects when seperation is min.
            min_dist: Minimum distance between objects a and b.
            time: Time at which the minimum distance occurs.
            location_a: Location of object a when distance is minimum
            location_b: Location of object b when distance is minimum
        """

        a, b, _ = self._get_relative_position_equation_constants()

        try:
            time = -b / (2 * a)  # Find time for local minima
        except ZeroDivisionError:  # When rocket and projectile have exactly equal velocity
            time = 0.0  # Distance between will be same at all times
        else:
            if time < 0:  # If the minimum occurs in the past, set min time to 0
                time = 0.0

        location_a = self._location(
            self.object_a_location, self.object_a_velocity, time
        )
        location_b = self._location(
            self.object_b_location, self.object_b_velocity, time
        )

        min_dist = location_a.distance2(location_b)

        return min_dist, time, (location_a, location_b)

    def times_objects_within_distance(
        self, distance: float
    ) -> Optional[
        Union[
            ObjectDistanceInfo, Tuple[Optional[ObjectDistanceInfo], ObjectDistanceInfo]
        ]
    ]:
        """Calculates the times and locations that objects a and b are a given distance apart.

        As the velocity of a and b are assumed to be constant, there are three different scenarios:
            - a and b are always further apart than the given distance (no solution)
            - a and b are a distance from each other at one time (1 solution)
            - a and b are a given distance from each other two times (2 solutions)
        If there is only 1 solution, then only one solution will be returned
        If the earlier of the two times is < 0, then None will be returned just for that time
        If both times are < 0, then None will be returned
        args:
            distance: Distance between objects a and b
        return:
            _: Information about the objects when they are a certain distance from one another:
                - Time
                - Location of a
                - Location of b
        """

        a, b, c = self._get_relative_position_equation_constants()
        c -= distance ** 2

        determinant = b ** 2 - 4 * a * c

        if determinant < 0:
            return None  # Distance is always greater

        t1_dist = (-b - math.sqrt(determinant)) / (2 * a)
        t2_dist = (-b + math.sqrt(determinant)) / (2 * a)

        t_max = max(t1_dist, t2_dist)
        if t_max < 0:
            return None  # Never within distance for positive time
        location_a_max = self.object_a_location + self.object_a_velocity * t_max
        location_b_max = self.object_b_location + self.object_b_velocity * t_max
        max_output = t_max, (location_a_max, location_b_max)

        if math.isclose(determinant, 0.0):
            return max_output  # Only one solution

        t_min = min(t1_dist, t2_dist)
        if t_min < 0:
            return None, max_output  # Already within distance at t = 0

        location_a_min = self.object_a_location + self.object_a_velocity * t_min
        location_b_min = self.object_b_location + self.object_b_velocity * t_min
        min_output = t_min, (location_a_min, location_b_min)

        return min_output, max_output

    def time_objects_first_within_distance(
        self, distance: float
    ) -> Optional[ObjectDistanceInfo]:
        """Calculates when and where objects a and b are first a given distance apart.

        If a and b are always further apart than the given distance, None will be returned
        If the first time a and b are already within distance of each other, None will be returned
        args:
            distance: Distance between objects a and b
        return:
            _: Information about the objects when they are a certain distance from one another:
                - Time
                - Location of a
                - Location of b
        TODO: A return of None can indicate one of two situations (unable to differentiate):
        """

        output = self.times_objects_within_distance(distance)

        if not output:
            return

        first, _ = output

        if type(first) is float:
            return output  # Only one solution; first refers to the time

        return first

    def _get_relative_position_equation_constants(self) -> Tuple[float, float, float]:
        """
        calculates the constants for the relative position quadratic equation

        For internal use only
        """

        x1 = self.object_b_velocity.x - self.object_a_velocity.x
        x2 = self.object_b_location.x - self.object_a_location.x
        y1 = self.object_b_velocity.y - self.object_a_velocity.y
        y2 = self.object_b_location.y - self.object_a_location.y

        a = x1 ** 2 + y1 ** 2
        b = 2 * (x1 * x2 + y1 * y2)
        c = x2 ** 2 + y2 ** 2

        return a, b, c
