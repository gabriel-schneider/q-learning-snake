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

    def keys(self):
        """Return all keys in the storage."""
        pass

    def clear(self):
        """Remove all data from the storage."""
        pass

    def remove(self, key):
        """Remove a key-value from storage."""
        pass

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

    def keys(self):
        return self._data.keys()

    def clear(self):
        self._data.clear()

    def remove(self, key):
        del self._data[key]

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
    def __init__(self, hostname, db=0):
        self._redis = redis.Redis(hostname, db=db)

    def get(self, key):
        return Decimal(self._redis.get(key).decode())

    def set(self, key, value):
        self._redis.set(key, value)

    def exists(self, key):
        return self._redis.exists(key)

    def keys(self):
        return self._redis.keys()

    def clear(self):
        self._redis.flushdb()

    def remove(self, key):
        self._redis.delete(key)

    def persist(self, filename):
        return True

    def load(self, filename):
        return True


class BaseMemoryTable(abc.ABC):
    def __init__(self, adapter: BaseMemoryStorageAdapter, actions: list):
        self._adapter = adapter
        self._actions = actions

    @property
    def adapter(self):
        return self._adapter

    def random(self):
        """Return a random action."""
        return random.choice(self._actions)

    def actions(self, state):
        """Return a list of weighted actions for a state."""
        return [[a, self.adapter.weight(state, a)] for a in self._actions]

    def exists(self, state):
        for action in self._actions:
            if self.adapter.weight(state, action) is not None:
                return True
        return False

    def choose(self, state):
        """Return a action for a state using probabilities."""
        if not self.exists(state):
            # self.initialize_state(state)
            print(f'{state} dont exists!')
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

    def initialize_state(self, state):
        """Create a list of weighted actions for a state."""
        actions = copy.deepcopy(self._actions)
        for action in actions:
            self.adapter.weight(state, action, Decimal('1'))

    def update(self, state, action, reward, next_state, learning, discount):
        """Update table data."""
        if not self.exists(state):
            self.initialize_state(state)

        weight = self.adapter.weight(state, action)
        weight = self._calculate_weight(
            weight, learning, discount, reward, self.best(next_state)[1])

        self.adapter.weight(state, action, weight)

    def _calculate_weight(self, weight, learning, discount, reward, next_weight):
        """Apply Q-learning update formula."""
        return (1 - learning) * weight + learning * (reward + discount * next_weight)

    def save(self, filename):
        """Persist/save table data in a file."""
        return self.adapter.persist(filename)

    def load(self, filename):
        return self.adapter.load(filename)


class SingleMemoryTable(BaseMemoryTable):
    pass


class DoubleMemoryTable(BaseMemoryTable):
    def __init__(self, adapter: BaseMemoryStorageAdapter, hidden_adapter: BaseMemoryStorageAdapter, actions: list, delay: int):
        super().__init__(adapter, actions)
        self._hidden_memory_table = SingleMemoryTable(hidden_adapter, actions)
        self._delay = 0
        self._max_delay = delay

    def _refresh(self):
        """Update active adapter with changes made in the hidden adapter."""
        print('Refreshing!!!')
        for key in self._hidden_memory_table.adapter.keys():
            self.adapter.set(key, self._hidden_memory_table.adapter.get(key))
        self._hidden_memory_table.adapter.clear()

    def update(self, state, action, reward, next_state, learning, discount):
        """Update table data."""

        for s in (state, next_state):
            if not self._hidden_memory_table.exists(s):
                if self.exists(s):
                    for a in self.actions(s):
                        self._hidden_memory_table.adapter.weight(
                            s, a[0], a[1])
                else:
                    self._hidden_memory_table.initialize_state(s)

        self._hidden_memory_table.update(
            state, action, reward, next_state, learning, discount)

        self._delay += 1
        if self._delay >= self._max_delay:
            self._delay = 0
            self._refresh()
