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

    def angle(self):
        return math.atan2(self.y, self.x)

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __str__(self):
        return f'Vector({self.x}, {self.y})'


class Snake:

    DEFAULT_POSITION = Vector(0, 0)
    DEFAULT_DIRECTION = Vector(1, 0)
    DEFAULT_LENGTH = 3

    def __init__(self, position=DEFAULT_POSITION, direction=DEFAULT_DIRECTION, length=DEFAULT_LENGTH):

        self._start_position = position
        self._start_direction = direction
        self._start_length = length

        self._body = []
        self._direction = None
        self._grow = 0

        self.reset()

    @property
    def position(self):
        return self._body[0]

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value

    def move(self):
        head = self._body[0]
        if self._grow:
            self._body.insert(
                0, Vector(head.x + self._direction.x, head.y + self._direction.y))
            self._grow -= 1
        else:
            for index, part in reversed(list(enumerate(self._body))):
                if index > 0:
                    self._body[index].x, self._body[index].y = self._body[index -
                                                                          1].x, self._body[index - 1].y
            head.x += self._direction.x
            head.y += self._direction.y

    def reset(self):
        self._body = [Vector(self._start_position)]
        self._direction = Vector(self._start_direction)
        self._grow = self._start_length - 1

    def __len__(self):
        return len(self._body)
