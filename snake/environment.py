import math
from decimal import Decimal
import pygame
import learning.environment
from learning import Memory
from snake.objects import Apple, Snake
from snake.math import Vector
from snake.world import World


class Environment(learning.environment.Environment):
    def __init__(self, agent, world, speed=60, reward=None):
        super().__init__(agent, reward)
        self._world = world

        self.score = 0
        self.objective = 0

        self._is_over = False

        self._display = None

        self._speed = speed
        self._clock = pygame.time.Clock()

    @property
    def world(self) -> World:
        return self._world

    def update(self):
        pygame.event.clear()

        self._clock.tick(self._speed)

        if self.world.check(self.world.snake.position, exclude=(Snake.VALUE, )) == self.world.WALL_VALUE:
            self._is_over = True
        else:
            for part in self.world.snake._body[1:]:
                if part == self.world.snake.position:
                    self._is_over = True

        if self.world.snake.position == self.world.apple.position:
            self.world.snake._grow += 1
            self.score += 1
            if self.score >= self.objective:
                self._is_over = True
                print('WIN!')
            self.world.apple.random()

        self.world.draw()
        self._display.blit(self.world.surface, (0, 0))
        pygame.display.flip()

    def initialize(self):
        size = self.world.to_px(self.world.size)
        self._display = pygame.display.set_mode((size, size))

        self.objective = sum(row.count(self.world.EMPTY_VALUE)
                             for row in self.world._structure) - 1 - self.world.snake._start_length

    def train(self, episodes, epsilon=0, output=True):
        self.initialize()

        for episode in range(episodes):
            self.reset()
            while not self.is_over():

                # Abort environment
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    return False
                state = self.observe()
                #print(f'{state} => {hash(state)}')
                action = self.agent.act(state, epsilon)
                self.world.snake.direction.rotate(
                    math.radians(90 * action.value))
                self.world.snake.move()
                self.update()
                new_state = self.observe()
                reward = self.reward(state, action, new_state)
                memory = Memory(state, action, reward, new_state)
                self.agent.remember(memory)
        return True

    def run(self, epsilon=0):
        self.initialize()

        while True:
            self.reset()
            while not self.is_over():
                # Abort environment
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    return False
                self.update()
                state = self.observe()
                action = self.agent.act(state, epsilon)
                self.world.snake.direction.rotate(
                    math.radians(90 * action.value))
                self.world.snake.move()
                reward = self.get_reward()
        return True

    def observe(self):
        def distance(x): return min(math.floor(round(x) / 2), 3)

        state = []
        direction = self.world.snake.direction.inverted()
        snake = self.world.snake.position
        for _ in range(3):
            direction.rotate(math.radians(90))
            value, position = self.world.raycast(
                snake, direction, (Apple.VALUE, Snake.VALUE, self.world.WALL_VALUE))

            state.append(
                (value, distance(snake.distance(position))))

        delta_vector = self.world.snake.position.inverted() + \
            self.world.apple.position
        delta = math.degrees(Vector.difference(
            self.world.snake.direction.angle, delta_vector.angle))

        state.append((
            round(delta / 45) * 45,
            distance(snake.distance(self.world.apple.position))
        ))
        return tuple(state)

    def is_over(self):
        return self._is_over

    def reset(self):
        self.world.reset()
        self._is_over = False
        self.score = 0
