import learning
from decimal import Decimal
from snake.objects import Snake, Apple


class DefaultReward(learning.environment.Reward):
    def __init__(self):
        self._last_score = 0

    def __call__(self, environment, state, action, state_prime):

        if environment.is_over():
            if environment.is_starving():
                return Decimal('-10.0')
            if environment.score < environment.objective:
                return Decimal('-10.0')
            print('WIN!!!')
            return Decimal('+10.0')

        if environment.score > self._last_score:
            self._last_score = environment.score
            return Decimal('+5.0')

        return Decimal('0.0')

    def reset(self):
        self._last_score = 0


class DistanceReward(DefaultReward):
    def __call__(self, environment, state, action, state_prime):
        reward = super().__call__(environment, state, action, state_prime)
        if float(reward) == 0:
            return Decimal(environment.world.snake.position.distance(environment.world.apple.position) / environment.world.size) * -1
        return reward
