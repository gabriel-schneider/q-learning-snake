import learning
from decimal import Decimal
from snake.objects import Snake, Apple


class DefaultReward(learning.environment.Reward):
    def __init__(self):
        self._last_score = 0

    def __call__(self, environment, state, action, state_prime):

        if environment.is_over():
            if environment.score < environment.objective:
                return Decimal('-50.0')
            return Decimal('100.0')

        if environment.score > self._last_score:
            self._last_score = environment.score
            return Decimal('20.0')

        return Decimal('0.0')

    def reset(self):
        self._last_score = 0
