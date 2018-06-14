import copy
import random
import math
import ast
from decimal import Decimal
import simplejson as json

from .environment import Action


class Agent:
    """Class to choose actions to execute in the environment."""

    def __init__(self, learning_rate, discount_factor, memory_table):
        self._learning_rate = learning_rate
        self._discount_factor = discount_factor
        self._memories = memory_table

    @property
    def memories(self):
        return self._memories

    def remember(self, state, action, reward, new_state):
        """Update agent memory table."""
        self.memories.update(state, action, reward, new_state,
                             self._learning_rate, self._discount_factor)

    def act(self, state, epsilon):
        """Act returning the best action for a certain state based on the Q Table."""
        if random.random() < epsilon:
            return self.memories.random()
        return self.memories.choose(state)

    @property
    def learning_rate(self):
        """Return agent learning rate."""
        return self._learning_rate

    @property
    def discount_factor(self):
        """Return agent discount factor."""
        return self._discount_factor

    def load(self, filename):
        """Load agent data from a file."""
        self.memories.load(filename)

    def save(self, filename):
        """Save agent data from a file."""
        self.memories.save(filename)
