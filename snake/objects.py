import copy
import random
import pygame
from snake.math import Vector


class Entity:
    """Represent a object in the world."""

    def __init__(self, world):
        self._world = world
        self._position = Vector(0, 0)

    @property
    def world(self):
        return self._world

    @property
    def position(self):
        """Return the position in the world."""
        return self._position

    def draw(self, surface):
        """Draw entity in the world."""
        pass

    def reset(self):
        """Reset entity to initial state."""
        pass


class Apple(Entity):

    VALUE = 4
    COLOR = pygame.Color(231, 76, 60)

    def random(self):
        position = copy.deepcopy(self.position)
        while self.world.check(position) != self.world.EMPTY_VALUE:
            position = Vector(random.randint(0, self.world.size),
                              random.randint(0, self.world.size))
        self._position = position

    def reset(self):
        return self.random()

    def draw(self, surface):
        rect = (self.world.to_px(self.position.x), self.world.to_px(
            self.position.y), self.world.unit_size, self.world.unit_size)
        pygame.draw.rect(surface, self.COLOR, rect)


class Snake(Entity):

    VALUE = 2
    DEFAULT_POSITION = Vector(0, 0)
    DEFAULT_DIRECTION = Vector(1, 0)
    DEFAULT_LENGTH = 3

    def __init__(self, world, position=DEFAULT_POSITION, direction=DEFAULT_DIRECTION, length=DEFAULT_LENGTH):
        super().__init__(world)
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

    def draw(self, surface):
        for index, part in enumerate(self._body):
            if index == 0:
                color = pygame.Color(44, 62, 80)
            else:
                color = pygame.Color(236, 240, 241)
            rect = (self.world.to_px(part.x), self.world.to_px(
                part.y), self.world.unit_size, self.world.unit_size)
            pygame.draw.rect(surface, color, rect)

    def is_colliding(self):
        """Return if the snake is colliding with a wall or herself."""
        if self.world.check(self.position, exclude=(self.VALUE, )) == self.world.WALL_VALUE:
            return True
        for part in self._body[1:]:
            if part == self.position:
                return True
        return False

    def __len__(self):
        return len(self._body)
