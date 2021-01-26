from dataclasses import dataclass
import math
from typing import List, Tuple, Union, Optional


@dataclass
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


@dataclass
class PolarCoordinate:
    r: float
    theta: float

    def pol2cart(self):
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)

        return Coordinate(x, y)
