import copy
import random
import math
import ast
from decimal import Decimal
import simplejson as json

from .environment import Action


class Agent:
    """Class to choose actions to execute in the environment."""

    def __init__(self, learning_rate, discount_factor, actions):
        self._learning_rate = learning_rate
        self._discount_factor = discount_factor
        self._memories = MemoryTable(actions)

    @property
    def memories(self):
        return self._memories

    def remember(self, memory):
        """Update agent memory table."""
        self.memories.update(memory, self._learning_rate,
                             self._discount_factor)

    def act(self, state, epsilon):
        """Act returning the best action for a certain state based on the Q Table."""
        if state not in self._memories.memories or random.random() < epsilon:
            return random.choice(self.memories.available_actions)
        return self.memories.choose(state)

    @property
    def learning_rate(self):
        """Return agent learning rate."""
        return self._learning_rate

    @property
    def discount_factor(self):
        """Return agent discount factor."""
        return self._discount_factor


class MemoryTable:
    """Implements the core Q-learning functionality."""

    def __init__(self, actions):
        self._memories = {}
        self._available_actions = copy.deepcopy(actions)
        for action in self._available_actions:
            action.weight = Decimal('1')

    @property
    def memories(self):
        """Return the memories dictionary."""
        return self._memories

    @property
    def available_actions(self):
        """Return all available actions."""
        return self._available_actions

    def get(self, state):
        """Return a list of actions available for a state."""
        return self._memories[state]

    def highest(self, state):
        """Alias for the greedy method."""
        return self.greedy(state)

    def greedy(self, state):
        """Return the best action object for a state."""
        if state not in self._memories.keys():
            return (Action(None, 'Undefined action', Decimal('1')))
        return max(self._memories[state], key=lambda a: a.weight)

    def choose(self, state):
        """Choose a random action object for a state using its weight as distribution."""
        actions = self.get(state)
        weights = [float(a.weight) for a in actions]
        temperature = 1
        sum_of_weights = sum([math.exp(w) / temperature for w in weights])
        probabilities = [math.exp(a.weight) / sum_of_weights for a in actions]
        return random.choices(actions, weights=probabilities)[0]

    def weight(self, state, action):
        """Return the weight of a action in a state."""
        return Action.with_value(self.get(state), action.value)

    def update(self, memory, learning_rate, discount_factor):
        """Update the Q-Table with new data."""
        if memory.state not in self._memories.keys():
            self._memories[memory.state] = copy.deepcopy(
                self._available_actions)

        action = Action.with_value(self.get(memory.state), memory.action.value)
        if action is not None:
            action.weight = (1 - learning_rate) * action.weight + learning_rate * (
                memory.reward + discount_factor * self.greedy(memory.state_prime).weight)
            return

    def save(self, filename):
        '''Save Q-Table to a JSON file.'''
        file = open(filename, 'w')
        table = {}
        for key, value in self._memories.memories.items():
            table[str(key)] = [[action.value, action.weight]
                               for action in value]

        json.dump(table, file)
        file.close()

    def load(self, filename):
        """Load Q-Table from a JSON file."""
        file = open(filename, 'r')
        table = json.load(file)

        # Create a value-description table for quick loading
        descriptions = {}
        for action in self.available_actions:
            descriptions[action.value] = action.description

        for state, actions in table.items():
            l = []
            for action in actions:
                value, weight = action[0], Decimal(action[1])
                l.append(Action(value, descriptions[value], weight))
            self._memories[ast.literal_eval(state)] = l
        file.close()


class Memory:
    """Collection of states, action and reward"""

    def __init__(self, state, action, reward, state_prime):
        self._state = state
        self._action = action
        self._reward = reward
        self._state_prime = state_prime

    @property
    def state(self):
        return self._state

    @property
    def action(self):
        return self._action

    @property
    def reward(self):
        return self._reward

    @property
    def state_prime(self):
        return self._state_prime

    def __hash__(self):
        return hash((self._state, self._action, self._reward, self._state_prime))
