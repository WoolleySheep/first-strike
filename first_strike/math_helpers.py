import math

from coordinate_classes import Coordinate


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


def distance_between_coordinates(coord1: Coordinate, coord2: Coordinate) -> float:

    return (coord2 - coord1).magnitude


def angle_from_a2b(coord1: Coordinate, coord2: Coordinate) -> float:

    return (coord2 - coord1).angle


def average(values):

    if not values:
        raise ValueError

    return sum(values) / len(values)


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
        return distance_between_coordinates(
            self.object_a_location, self.object_b_location
        )

    @property
    def angle_a2b(self):
        return angle_from_a2b(self.object_a_location, self.object_b_location)

    def angle_b2a(self):
        return angle_from_a2b(self.object_b_location, self.object_a_location)

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

        min_dist = distance_between_coordinates(
            location_a_min_dist, location_b_min_dist
        )

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
