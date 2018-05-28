import json
import copy
import math
import random
import pygame

from learning import Environment, Memory
from snake import Snake, Vector

from decimal import *


class SnakeGame(Environment):

    DATA_EMPTY = 0
    DATA_WALL = 1
    DATA_SNAKE = 2
    DATA_APPLE = 4

    UNIT_SIZE = 32

    def __init__(self, agent, world_name='default', world_directory='data/worlds', ticks=5):
        super().__init__(agent)

        self._abort = False
        self._is_over = False
        self._ticks = ticks
        self._colors = {
            self.DATA_WALL:         pygame.Color(40, 40, 40),
            self.DATA_EMPTY:        (pygame.Color(39, 174, 96), pygame.Color(46, 204, 113)),
            self.DATA_SNAKE:        pygame.Color(52, 152, 219),
            self.DATA_APPLE:        pygame.Color(231, 76, 60)
        }

        # World
        self._size = 0
        self._data = []
        self._initial_data = []
        self._world_directory = world_directory
        self._world_surface = None

        self._score = 0
        self._objective = 0

        self._snake = Snake()
        self._apple = Vector(0, 0)

        self.load(world_name)

    @property
    def snake(self):
        return self._snake

    @property
    def apple(self):
        return self._apple

    def load_from(self, filename):
        """Load a world from a file."""
        return self._load(filename)

    def load(self, world_name):
        """Load a world from the worlds directory."""
        return self._load(f'{self._world_directory}/{world_name}.json')

    def _load(self, filename):
        """Load a world from a file."""
        with open(filename, 'r') as file:
            world = json.load(file)
            self._size = world['size']
            self._initial_data = world['data']
            self._data = copy.deepcopy(self._initial_data)

            if 'snake' in world.keys():
                snake = world['snake']
                self._snake = Snake(Vector(snake['position']), Vector(
                    snake['direction']), snake['length'])

            self._objective = 0
            for x in range(self._size):
                for y in range(self._size):
                    if self._data[x][y] == self.DATA_EMPTY:
                        self._objective += 1

    def start_up(self):
        """Start pygame and output options."""
        pygame.init()
        self._clock = pygame.time.Clock()
        display_size = self._size * self.UNIT_SIZE
        self._display = pygame.display.set_mode((display_size, display_size))

        self._build_world()
        self._update()

    def _build_world(self):
        """Generate the world data into a pygame surface."""
        self._world_surface = pygame.Surface(self._display.get_size())
        for x in range(self._size):
            for y in range(self._size):
                value = self._data[x][y]
                if isinstance(self._colors[value], tuple):
                    colors = self._colors[value]
                    color = colors[(x + y) % len(colors)]
                else:
                    color = self._colors[value]
                pygame.draw.rect(self._world_surface, color, (x * self.UNIT_SIZE,
                                                              y * self.UNIT_SIZE, self.UNIT_SIZE, self.UNIT_SIZE))

    def explain(self, state):
        """Explain the current state"""
        pass

    def _update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_over = True
                return

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    self._ticks = 1
                elif event.key == pygame.K_2:
                    self._ticks = 5
                elif event.key == pygame.K_3:
                    self._ticks = 15
                elif event.key == pygame.K_4:
                    self._ticks = 30
                elif event.key == pygame.K_5:
                    self._ticks = 60
                elif event.key == pygame.K_6:
                    self._ticks = -1
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    self._is_over = True
                    self._abort = True
                    return

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pos = tuple(map(lambda x: math.floor(
                        x / self.UNIT_SIZE), pygame.mouse.get_pos()))
                    x, y = pos[0], pos[1]
                    value = self._data[x][y]
                    value = self.DATA_EMPTY if value == self.DATA_WALL else self.DATA_WALL
                    self._data[x][y] = value
                    self._initial_data[x][y] = value
                    self._build_world()
        self._draw()
        pygame.display.flip()

    def _draw(self):
        self._clock.tick(self._ticks)
        self._display.blit(self._world_surface, (0, 0))
        for index, part in enumerate(self._snake._body):
            color = pygame.Color(
                142, 68, 173) if index == 0 else pygame.Color('white')
            pygame.draw.rect(self._display, color, (part.x * self.UNIT_SIZE,
                                                    part.y * self.UNIT_SIZE, self.UNIT_SIZE, self.UNIT_SIZE))
        pygame.draw.rect(self._display, pygame.Color(231, 76, 60), (self._apple.x *
                                                                    self.UNIT_SIZE, self._apple.y * self.UNIT_SIZE, self.UNIT_SIZE, self.UNIT_SIZE))

    def _check_world(self, x=0, y=0, at=None):
        """Return the object at a specific world position"""
        if isinstance(x, Vector):
            at = x

        if at is not None:
            x = at.x
            y = at.y

        for part in self._snake._body:
            if part.x == x and part.y == y:
                return self.DATA_SNAKE

        if self._apple.x == x and self._apple.y == y:
            return self.DATA_APPLE

        try:
            return self._data[x][y]
        except IndexError:
            return -1

    def _raycast_world(self, position, direction, valid):
        """Raycast from a initial point in a direction against the environment world data"""
        position = Vector(position.x, position.y)
        position.x += direction.x
        position.y += direction.y
        while self._check_world(at=position) not in valid:
            if self._check_world(at=position) == -1:
                return (-1, position)
            position.x += direction.x
            position.y += direction.y
        return (self._check_world(at=position), position)

    def observe(self):

        sensors = []
        direction = self._snake.direction.inverted()
        for _ in range(7):
            direction.rotate(math.radians(45))
            value, position = self._raycast_world(self._snake.position(
            ), direction, (self.DATA_APPLE, self.DATA_SNAKE, self.DATA_WALL))

            v = min(math.floor(
                round(self._snake.position().distance(position)) / 2), 3)
            sensors.append((value, v))
        return tuple(sensors)

    def reset(self):

        self._score = 0
        self._is_over = False
        self._data = copy.deepcopy(self._initial_data)
        self._snake.reset()
        self._move_apple()

    def _move_apple(self):
        '''Move apple to a random position'''
        pos = self._apple
        while self._check_world(pos) != self.DATA_EMPTY:
            pos = Vector(random.randint(0, self._size),
                         random.randint(0, self._size))
        self._apple = pos

    def get_reward(self):

        for part in self._snake._body[1:]:
            if part == self._snake.position():
                self._is_over = True
                return Decimal('-10.0')

        if self._data[self._snake.position().x][self._snake.position().y] == self.DATA_WALL:
            self._is_over = True
            return Decimal('-10.0')

        if self._snake.position() == self._apple:
            self._move_apple()
            self._snake._grow += 1
            self._score += 1
            if self._score >= self._objective:
                self._is_over = True
                return Decimal('10.0')
            return Decimal('5.0')
        # -round(self._snake.position().distance(self._apple)) / 16
        return Decimal('0')

    def is_over(self):
        return self._is_over

    def train(self, episodes, epsilon=0, output=True):
        if output:
            self.start_up()
        for episode in range(episodes):
            if self._abort:
                return
            self.reset()
            while not self.is_over() and not self._abort:
                state = self.observe()
                if output:
                    self._update()

                action = self.agent.act(state, 0)

                self._snake.direction.rotate(
                    math.radians(90 * action.value))
                self._snake.move()

                reward = self.get_reward()

                new_state = self.observe()

                self.agent.remember(
                    Memory(state, action, reward, new_state))
        if output:
            pygame.quit()

    def run(self, epsilon=0, output=True):
        if output:
            self.start_up()
        while not self._abort:
            self.reset()
            while not self.is_over():
                state = self.observe()
                if output:
                    self._update()

                action = self.agent.act(state, 0)

                self._snake.direction.rotate(
                    math.radians(90 * action.value))
                self._snake.move()

                self.get_reward()
