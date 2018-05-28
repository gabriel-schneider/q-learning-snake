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
    # agent.memories.load('data/memories/memories_20180527200821.json')

    # Create the snake game environment
    environment = SnakeGame(agent, 'close')

    # Train it
    environment.train(500)

    date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    agent.memories.save(f'data/memories/memories_{date}.json')
