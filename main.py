import math
import json
import datetime
import pygame
from decimal import *

from learning import Agent, Action, Memory
from environments import SnakeGame

if __name__ == '__main__':
    # Define witch actions are available

    actions = [
        Action(-1, 'Turn Left'),
        Action(0, 'Go Foward',),
        Action(1, 'Turn Right')
    ]

    # Create a agent with the available actions
    agent = Agent(Decimal(0.9), Decimal(0.75), actions)
    agent.memories.load('data/memories/memories_20180527200821.json')
    learning = True

    # Create the snake game environment
    environment = SnakeGame(agent, 'close')

    # Train it
    episodes = 100
    for episode in range(episodes):
        print(f'Episode {episode}')
        pygame.display.set_caption(f'{episode}')
        environment.reset()
        while not environment.is_over():
            state = environment.observe()
            print(state, environment._score, environment._objective)
            if environment.output:
                environment._update()

            # Agent select a action, that is, select which direction to turn
            action = agent.act(state, 0)

            # Agent execute the action, turn and move
            environment._snake._direction.rotate(
                math.radians(90 * action.value))
            environment._snake.move()

            # Agent receive a reward for its action
            reward = environment.get_reward()

            if learning:
                # Agent enter a new state
                new_state = environment.observe()

                # Agent remember updating his Q-Table
                environment.agent.remember(
                    Memory(state, action, reward, new_state))

    if learning:
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        agent.memories.save(f'data/memories/memories_{date}.json')
