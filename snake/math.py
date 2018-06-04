import math


class Vector:
    def __init__(self, x=0, y=0):
        if isinstance(x, (list, tuple)):
            self.x = x[0]
            self.y = x[1]
        elif isinstance(x, __class__):
            self.x = x.x
            self.y = x.y
        else:
            self.x = x
            self.y = y

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return (self.x == other.x) and (self.y == other.y)

    def __ne__(self, other):
        return (self.__eq__(other) == False)

    def rotated(self, angle):
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Vector(round(x), round(y))

    def rotate(self, angle):
        vector = self.rotated(angle)
        self.x = vector.x
        self.y = vector.y
        return self

    def inverted(self):
        return Vector(self.x * -1, self.y * -1)

    def invert(self):
        self.x *= -1
        self.y *= -1
        return self

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    @staticmethod
    def difference(alpha, beta):
        a = beta - alpha
        if a > math.radians(180):
            a -= math.radians(360)
        elif a < math.radians(-180):
            a += math.radians(360)
        return a

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __str__(self):
        return f'Vector({self.x}, {self.y})'
