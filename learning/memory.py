import abc
import copy
import random
import math
import redis
import simplejson as json
from decimal import Decimal
import itertools


class BaseMemoryStorageAdapter(abc.ABC):
    def get(self, key):
        """Return a key value."""
        pass

    def set(self, key, value):
        """Define a value to a key."""
        pass

    def exists(self, key):
        """Return if a key exists."""
        pass

    def persist(self, filename):
        """Persist data into a file."""
        pass

    def load(self, filename):
        """Load data from a file."""
        pass

    ###

    def weight(self, state, action, weight=None):
        """Return or set the weight for a action in state."""
        key = f'{state}_{action}'
        if weight is not None:
            return self.set(key, weight)
        elif self.exists(key):
            return self.get(key)
        return None


class DictMemoryStorageAdapter(BaseMemoryStorageAdapter):
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data[key]

    def set(self, key, value):
        self._data[key] = value

    def exists(self, key):
        return key in self._data

    def persist(self, filename):
        with open(filename, 'w') as file:
            json.dump({str(k): v for k, v in self._data.items()}, file)
        return True

    def load(self, filename):
        self._data.clear()
        with open(filename, 'r') as file:
            data = json.load(file)
            for key, value in data.items():
                self._data[key] = Decimal(value)
                # self._data[key] = list(
                #     map(lambda x: [x[0], Decimal(x[1])], value))
        return True


class RedisMemoryStorageAdapter(BaseMemoryStorageAdapter):
    def __init__(self, hostname):
        self._redis = redis.Redis(hostname)

    def get(self, key):
        return Decimal(self._redis.get(key).decode())

    def set(self, key, value):
        self._redis.set(key, value)

    def exists(self, key):
        return self._redis.exists(key)

    def persist(self, filename):
        return True

    def load(self, filename):
        return True


class BaseMemoryTable(abc.ABC):
    def __init__(self, adapter: BaseMemoryStorageAdapter, actions: list):
        self._adapter = adapter
        self._actions = actions

    def random(self):
        """Return a random action."""
        return random.choice(self._actions)

    def actions(self, state):
        """Return a list of weighted actions for a state."""
        return [[a, self._adapter.weight(state, a)] for a in self._actions]

    def exists(self, state):
        for action in self._actions:
            if self._adapter.weight(state, action) is not None:
                return True
        return False

    def choose(self, state):
        """Return a action for a state using probabilities."""
        if not self.exists(state):
            self._initialize_state(state)
            return self.random()

        actions = self.actions(state)
        weights = [float(a[1]) for a in actions]
        sum_of_weights = sum([math.exp(w) for w in weights])
        probabilities = [math.exp(a[1]) / sum_of_weights for a in actions]
        return random.choices([a[0] for a in actions], weights=probabilities)[0]

    def best(self, state):
        """Return a weighted-action for a state with highest weight."""
        if self.exists(state):
            return max(self.actions(state), key=lambda x: x[1])
        return [None, Decimal('1')]

    def _initialize_state(self, state):
        """Create a list of weighted actions for a state."""
        actions = copy.deepcopy(self._actions)
        for action in actions:
            self._adapter.weight(state, action, Decimal('1'))

    def update(self, state, action, reward, next_state, learning, discount):
        """Update table data."""
        if not self.exists(state):
            self._initialize_state(state)

        actions = self.actions(state)

        for act in actions:
            if act[0] == action:
                act[1] = (1 - learning) * act[1] + learning * \
                    (reward + discount * self.best(next_state)[1])
                self._adapter.weight(state, action, act[1])
                break
#        self._adapter.set(state, actions)

    def save(self, filename):
        """Persist/save table data in a file."""
        return self._adapter.persist(filename)

    def load(self, filename):
        return self._adapter.load(filename)


class SingleMemoryTable(BaseMemoryTable):
    pass


class DoubleMemoryTable(BaseMemoryTable):
    pass
