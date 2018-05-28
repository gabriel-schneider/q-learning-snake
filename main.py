import datetime
import argparse
from decimal import *

from learning import Agent, Action
from environments import SnakeGame

DEFAULT_LEARN = 0.6
DEFAULT_DISCOUNT = 0.9
DEFAULT_WORLD = 'default'
DEFAULT_EPISODES = 100

# Define witch actions are available
ACTIONS = [
    Action(-1, 'Turn Left'),
    Action(0, 'Go Foward',),
    Action(1, 'Turn Right')
]


def train(args):

    learn = Decimal(args.learn)
    discount = Decimal(args.discount)
    world = args.world

    # Create a agent with the available actions
    agent = Agent(Decimal(learn), Decimal(discount), ACTIONS)

    date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if args.memory is not None:
        try:
            print(f'Importing existing memories from {args.memory}...')
            agent.memories.load(f'data/memories/{args.memory}.json')
            print('Done!')
        except FileNotFoundError:
            print(
                f'File {args.memory} not found, creating a new one...')
    else:
        args.memory = f'memories_{date}'

    # Create the snake game environment
    environment = SnakeGame(agent, world)

    print('Parameters:\n')
    print(f'\t Learning Rate: {round(learn, 3)}')
    print(f'\t Discount Factor: {round(discount, 3)}')
    print(f'\t Episodes: {args.episodes}')
    print('\nStarting...')

    # Train it
    environment.train(args.episodes)

    print('Saving...')
    agent.memories.save(f'data/memories/{args.memory}.json')
    print('Done.')


def run(args):

    world = args.world

    # Create a agent with the available actions
    agent = Agent(0, 0, ACTIONS)

    try:
        print(f'Importing existing memories from {args.memory}...')
        agent.memories.load(f'data/memories/{args.memory}.json')
        print('Done!')
    except FileNotFoundError:
        print(f'File {args.memory} not found, cannot continue...')
        exit(0)

    environment = SnakeGame(agent, world)

    print('\nStarting...')

    environment.run()

    print('Done.')


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Training
train_parser = subparsers.add_parser('train')
train_parser.add_argument(
    '--learn', type=float, default=DEFAULT_LEARN, help='Learnig Rate')
train_parser.add_argument('--discount', type=float,
                          default=DEFAULT_DISCOUNT, help='Discount Factor')
train_parser.add_argument(
    '--memory', type=str, default=None, help='Memory JSON filename')
train_parser.add_argument(
    '--world', type=str, default=DEFAULT_WORLD, help='World JSON filename')
train_parser.add_argument(
    '--episodes', type=int, default=DEFAULT_EPISODES, help='Number of episodes to train')
train_parser.set_defaults(func=train)

# Running
run_parser = subparsers.add_parser('run')
run_parser.add_argument(
    '--memory', type=str, help='Memory JSON filename')
run_parser.add_argument(
    '--world', type=str, default=DEFAULT_WORLD, help='World JSON filename')
run_parser.set_defaults(func=run)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
