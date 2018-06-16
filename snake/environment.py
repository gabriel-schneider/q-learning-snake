import copy
import math
import statistics
import pygame
import learning
from snake.objects import Apple, Snake
from snake.math import Vector
from snake.world import World
from snake.rewards import DefaultReward


class Results(learning.environment.Results):
    def __init__(self):
        super().__init__()
        self.episodes = 0
        self.steps = []
        self.wins = 0
        self.loses = 0
        self.scores = []
        self.starves = 0

    def __repr__(self):
        data = [
            f'\t=> Episodes: {self.episodes}',
            f'\t=> Steps Average: {statistics.mean(self.steps):0.2f}',
            f'\t=> Score Average: {statistics.mean(self.scores):0.2f}',
            f'\t=> Wins: {self.wins}',
            f'\t=> Loses: {self.loses}'
        ]
        return '\n'.join(data)


class Environment(learning.environment.Environment):

    def __init__(self, agent, world, speed=60, reward=None):
        super().__init__(agent, reward)
        self._world = world

        self.score = 0
        self.objective = 0
        self._starving = 0
        self._max_starving = 100

        self._is_over = False

        self._display = None

        self._speed = speed
        self._clock = pygame.time.Clock()

        if self._reward_model is None:
            self._reward_model = DefaultReward()

    @property
    def world(self) -> World:
        return self._world

    def is_starving(self):
        return self._starving >= self._max_starving

    def update(self, results, output):
        if output:
            pygame.event.clear()
            self._clock.tick(self._speed)

        self._is_over = self.world.snake.is_colliding() or self.is_starving()
        if self._is_over:
            results.loses += 1
            if self.is_starving():
                results.starves += 1

        if self.world.snake.position == self.world.apple.position:
            self._starving = 0
            self.world.snake._grow += 1
            self.score += 1
            if self.score >= self.objective:
                self._is_over = True
                results.wins += 1
            self.world.apple.random()
        else:
            self._starving += 1

    def draw(self):
        self.world.draw()
        self._display.blit(self.world.surface, (0, 0))
        pygame.display.flip()

    def initialize(self, output):
        if output:
            size = self.world.to_px(self.world.size)
            self._display = pygame.display.set_mode((size, size))

        self.objective = sum(row.count(self.world.EMPTY_VALUE)
                             for row in self.world._structure) - 1 - self.world.snake._start_length

    def train(self, episodes, epsilon=0, output=True):
        self.initialize(output)
        results = Results()
        for episode in range(episodes):
            if results.abort:
                break

            self.reset()
            results.episodes = episode
            steps = 0

            # Enquanto o estado do ambiente não for terminal
            while not self.is_over():
                steps += 1
                if output:
                    self.draw()

                if output:
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        results.abort = True
                        break
                state = self.observe()

                action = self.agent.act(state, epsilon)

                self.world.snake.direction.rotate(
                    math.radians(90 * action))
                self.world.snake.move()
                self.update(results, output)
                new_state = self.observe()
                reward = self.reward(state, action, new_state)
                self.agent.remember(state, action, reward, new_state)
            results.scores.append(self.score)
            results.steps.append(steps)
        return results

    def run(self, epsilon=0):
        self.initialize(True)
        results = Results()
        while results.abort is False:
            self.reset()
            results.episodes += 1
            steps = 0
            while not self.is_over():
                steps += 1
                self.draw()

                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    results.abort = True
                    break

                state = self.observe()
                action = self.agent.act(state, epsilon)
                self.world.snake.direction.rotate(
                    math.radians(90 * action.value))
                self.world.snake.move()
                self.update(results, True)
            results.scores.append(self.score)
            results.steps.append(steps)
        return results

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
        if callable(self._reward_model):
            self._reward_model.reset()
        self.world.reset()
        self._is_over = False
        self.score = 0
        self._starving = 0
