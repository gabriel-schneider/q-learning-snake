import copy
import pygame
import simplejson as json
from snake.math import Vector
from snake.objects import Snake, Apple


class WorldNotLoadedError(Exception):
    pass


class World:

    UNKNOW_VALUE = -1
    WALL_VALUE = 1
    EMPTY_VALUE = 0

    WALL_COLOR = pygame.Color(30, 30, 30)
    EMPTY_COLOR = (pygame.Color(39, 174, 96), pygame.Color(46, 204, 113))

    def __init__(self, directory=None, unit_size=16):

        # Entities
        self._snake = None
        self._apple = None

        self._directory = directory
        self._structure = []
        self._structure_surface = None
        self._surface = None

        self.name = ''
        self.size = 0

        self._unit_size = unit_size

    @property
    def unit_size(self):
        return self._unit_size

    @property
    def surface(self):
        return self._surface

    @property
    def snake(self):
        return self._snake

    @property
    def apple(self):
        return self._apple

    @property
    def loaded(self):
        return self._structure and self.size > 0

    def snapshot(self):
        structure = ''
        for row in self._structure:
            for value in row:
                structure += str(value)

        snake = '|'.join([f'{p.x};{p.y}' for p in self.snake._body])

        apple = f'{self.apple.position.x};{self.apple.position.y}'

        return '-'.join([structure, snake, apple])

    def to_px(self, value):
        if isinstance(value, (tuple, list)):
            return map(self.to_px, value)
        return value * self.unit_size

    def check(self, position, exclude=None):
        """Return the value of the world position."""
        if exclude is None:
            exclude = tuple()

        # Snake
        if self.snake.VALUE not in exclude:
            for part in self.snake._body:
                if position == part:
                    return self.snake.VALUE

        if self.apple.VALUE not in exclude:
            if position == self.apple.position:
                return self.apple.VALUE

        try:
            return self._structure[position.x][position.y]
        except IndexError:
            return self.UNKNOW_VALUE

    def raycast(self, position, direction, mask):
        """Raycast from the position in the given direction returning a entity in the mask."""
        ray_position = copy.deepcopy(position) + direction
        mask = mask + (self.UNKNOW_VALUE, )

        while self.check(ray_position) not in mask:
            ray_position = ray_position + direction
        return (self.check(ray_position), ray_position)

    def _create_surfaces(self):
        """Create the surfaces used by the world."""
        if not self.loaded:
            raise WorldNotLoadedError(
                'The world must be loaded before creating surfaces of it!')

        size = self.to_px(self.size)
        self._surface = pygame.Surface((size, size))
        self._structure_surface = pygame.Surface((size, size))

    def _build_structure(self):
        for x in range(self.size):
            for y in range(self.size):
                if self._structure[x][y] == self.WALL_VALUE:
                    color = self.WALL_COLOR
                else:
                    color = self.EMPTY_COLOR[(x + y) % 2]
                rect = (self.to_px(x), self.to_px(y),
                        self.unit_size, self.unit_size)
                pygame.draw.rect(self._structure_surface, color, rect)

    def draw(self):
        """Draw the current world."""
        self._surface.blit(self._structure_surface, (0, 0))
        self.apple.draw(self._surface)
        self.snake.draw(self._surface)

    def load(self, name):
        """Load a existing world from file."""
        filename = f'{self._directory}/{name}.json'
        with open(filename, 'r') as file:
            world = json.load(file)

        self.size = world['size']
        self._structure = copy.deepcopy(world['data'])

        if 'snake' in world.keys():
            snake = world['snake']
            position = Vector(snake['position'])
            direction = Vector(snake['direction'])
            length = snake['length']
            self._snake = Snake(self, position, direction, length)
        else:
            self._snake = Snake(self)

        self._apple = Apple(self)

        self._create_surfaces()
        self._build_structure()

        self.reset()
        # After loading we should generate the surfaces, build
        # the structure surface and reset the world.

    def save(self, name):
        """Save the current world to file."""
        pass

    def reset(self):
        self.snake.reset()
        self.apple.reset()
