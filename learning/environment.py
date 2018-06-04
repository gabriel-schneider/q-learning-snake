class Environment:

    def __init__(self, agent, reward=None):
        self._agent = agent
        self._reward_model = reward

    @property
    def agent(self):
        """Return the agent object."""
        return self._agent

    def observe(self):
        """Return the environment current state."""
        pass

    def reset(self):
        """Reset the environment to a initial state."""
        pass

    def _update(self):
        """Update the environment."""
        pass

    def _draw(self):
        """Draw the environment."""
        pass

    def reward(self, state, action, state_prime):
        """Return a reward value using the reward model."""
        if callable(self._reward_model):
            return self._reward_model(self, state, action, state_prime)
        return self._reward_model

    def is_over(self):
        """Return if the current environment state should end the episode."""
        pass

    def run(self, epsilon=0, output=True):
        """Run the environment without training the agent."""
        pass

    def train(self, episodes, epsilon=0, output=True):
        """Run the environment training the agent."""
        pass


class Reward:
    def __call__(self, environment, state, action, state_prime):
        pass


class Action:
    """Represent a action that the agnet can execute in the environment."""

    def __init__(self, value, description, weight=0):
        self._value = value
        self._description = description
        self._weight = weight

    @property
    def value(self):
        return self._value

    @property
    def description(self):
        return self._description

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    def execute(self, subject):
        """Execute the action."""
        pass

    def __str__(self):
        return f'Action(description={self._description}, value={self._value}, weight={self.weight})'

    @staticmethod
    def with_value(actions, value):
        """Find and return a particular action in a list of action with a specific value."""
        for action in actions:
            if action.value == value:
                return action
        return None
