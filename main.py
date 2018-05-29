import datetime
import argparse
from decimal import *
import simplejson as json
import pygame
from learning import Agent, DoubleAgent, Action
from environments import SnakeGame

DEFAULT_LEARN = 0.6
DEFAULT_DISCOUNT = 0.9
DEFAULT_WORLD = 'default'
DEFAULT_EPISODES = 100
DEFAULT_SPEED = 30
DEFAULT_REPEAT = 1

# Define witch actions are available
ACTIONS = [
    Action(-1, 'Turn Left'),
    Action(0, 'Go Foward',),
    Action(1, 'Turn Right')
]


def train(args):

    learn = args.learn
    discount = args.discount
    repeat = args.repeat

    if args.config is not None:
        with open(f'data/training/{args.config}.json', 'r') as file:
            config = json.load(file)
            worlds = config['worlds']
            learn = Decimal(config.get('learning', DEFAULT_LEARN))
            discount = Decimal(config.get('discount', DEFAULT_DISCOUNT))
            repeat = config.get('repeat', DEFAULT_REPEAT)

    if learn is None:
        learn = DEFAULT_LEARN

    if discount is None:
        discount = DEFAULT_DISCOUNT

    if repeat is None:
        repeat = DEFAULT_REPEAT

    world = args.world

    # Create a agent with the available actions
    agent = DoubleAgent(Decimal(learn), Decimal(discount), ACTIONS)

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

    print('Parameters:\n')
    print(f'\t Learning Rate: {round(learn, 3)}')
    print(f'\t Discount Factor: {round(discount, 3)}')
    if repeat == -1:
        print(f'\t Repeat: forever')
    else:
        print(f'\t Repeat: {repeat} times')
    print('\nStarting...')

    if args.config is None:
        worlds = [
            {
                'name': args.world,
                'episodes': args.episodes
            }
        ]

    episodes_total = 0
    try:
        while repeat != 0:
            for world in worlds:
                name, episodes = world['name'], world['episodes']
                pygame.display.set_caption(f'{name} - {episodes}')
                print(
                    f'Training at {name} for {episodes} episodes... ({episodes_total})')
                environment = SnakeGame(agent, name, ticks=args.speed)
                environment.train(episodes)
                episodes_total += episodes
                if environment._abort:
                    break
            if environment._abort:
                break
            repeat -= 1
    except KeyboardInterrupt:
        pygame.quit()

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


def editor(args):
    environment = SnakeGame(None, args.world, ticks=60, editor=True)
    environment.start_up()
    while not environment.is_over():
        environment._update()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Training
train_parser = subparsers.add_parser('train')
train_parser.add_argument(
    '--learn', type=float, default=None, help='Learnig Rate')
train_parser.add_argument('--discount', type=float,
                          default=None, help='Discount Factor')
train_parser.add_argument(
    '--memory', type=str, default=None, help='Memory JSON filename')
train_parser.add_argument(
    '--world', type=str, default=DEFAULT_WORLD, help='World JSON filename')
train_parser.add_argument(
    '--episodes', type=int, default=DEFAULT_EPISODES, help='Number of episodes to train')
train_parser.add_argument(
    '--config', type=str, default=None, help='Config JSON file for training')
train_parser.add_argument(
    '--speed', type=int, default=DEFAULT_SPEED, help='Speed to visualize the training')
train_parser.add_argument(
    '--repeat', type=int, default=None, help='How many times the training will be repeated')
train_parser.set_defaults(func=train)


# Running
run_parser = subparsers.add_parser('run')
run_parser.add_argument(
    '--memory', type=str, help='Memory JSON filename')
run_parser.add_argument(
    '--world', type=str, default=None, help='World JSON filename')
run_parser.set_defaults(func=run)

# Editor
editor_parser = subparsers.add_parser('editor')
editor_parser.add_argument(
    '--world', type=str, help='World JSON filename')
editor_parser.set_defaults(func=editor)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
