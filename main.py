import datetime
import argparse
from decimal import *
import simplejson as json
import pygame
from learning import Agent, DoubleAgent, Action
from snake import Environment, World
import os.path

DEFAULT_LEARN = 0.6
DEFAULT_DISCOUNT = 0.9
DEFAULT_WORLD = 'default'
DEFAULT_EPISODES = 100
DEFAULT_SPEED = 30
DEFAULT_CYCLE = 1

# Define witch actions are available
ACTIONS = [
    Action(-1, 'Turn Left'),
    Action(0, 'Go Foward',),
    Action(1, 'Turn Right')
]


def train(args):

    learn = args.learn
    discount = args.discount
    cycles = args.cycles

    if args.config is not None:
        with open(f'data/training/{args.config}.json', 'r') as file:
            config = json.load(file)
            worlds = config['worlds']
            learn = Decimal(config.get('learning', DEFAULT_LEARN))
            discount = Decimal(config.get('discount', DEFAULT_DISCOUNT))
            cycles = config.get('repeat', DEFAULT_CYCLE)
    else:
        worlds = [{
            'name': args.world,
            'episodes': args.episodes
        }]

    if learn is None:
        learn = DEFAULT_LEARN

    if discount is None:
        discount = DEFAULT_DISCOUNT

    if cycles is None:
        cycles = DEFAULT_CYCLE

    world = args.world

    agent = DoubleAgent(Decimal(learn), Decimal(discount), ACTIONS)

    date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if args.memory is not None:
        filename = f'data/memories/{args.memory}.json'
        if os.path.isfile(filename):
            try:
                print(
                    f'Importing existing memories from "{args.memory}"... ', end='')
                agent.load(filename)
                print('Done!')
            except json.JSONDecodeError as exception:
                print(
                    f'File {args.memory} could not be loaded!')
                print(exception)
    else:
        args.memory = f'memories_{date}'
        print(f'Memories will be saved in "{args.memory}"')

    print('Parameters:\n')
    print(f'\t Learning Rate: {round(learn, 3)}')
    print(f'\t Discount Factor: {round(discount, 3)}')
    if cycles == -1:
        print(f'\t Cycles: endless')
    else:
        print(f'\t Cycles: {cycles} times')
    print('\nStarting...')

    world = World('data/worlds', args.unit_size)
    environment = Environment(agent, world, speed=args.speed)
    episodes_count = 0
    status = True
    while cycles != 0 and status:
        for world in worlds:
            name, episodes = world['name'], world['episodes']
            episodes_count += episodes
            print(
                f'Training at {name} for {episodes} episodes... ({episodes_count})')
            environment.world.load(name)
            status = environment.train(episodes, args.epsilon)
            if not status:
                pygame.quit()
                break
        cycles -= 1

    print('Saving memories... ', end='')
    agent.memories.save(f'data/memories/{args.memory}.json')
    print('Done.')


def run(args):

    agent = Agent(0, 0, ACTIONS)

    try:
        print(f'Importing existing memories from {args.memory}...', end='')
        agent.memories.load(f'data/memories/{args.memory}.json')
        print('Done!')
    except FileNotFoundError:
        print(f'File {args.memory} not found, cannot continue...')
        exit(1)

    world = World('data/worlds', args.unit_size)
    environment = Environment(agent, world, speed=args.speed)
    world.load(args.world)
    print('\nStarting...')

    environment.run(epsilon=args.epsilon)

    print('Done.')


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Training
train_parser = subparsers.add_parser('train')
train_parser.add_argument(
    '--learn', type=float, default=None, help='Learnig Rate')
train_parser.add_argument('--discount', type=float,
                          default=None, help='Discount Factor')
train_parser.add_argument(
    '--memory', type=str, default=None, help='Memory filename')
train_parser.add_argument(
    '--world', type=str, default=DEFAULT_WORLD, help='World name')
train_parser.add_argument(
    '--episodes', type=int, default=DEFAULT_EPISODES, help='Number of episodes to train')
train_parser.add_argument(
    '--config', type=str, default=None, help='Training configuration file')
train_parser.add_argument(
    '--speed', type=int, default=DEFAULT_SPEED, help='Environment speed')
train_parser.add_argument(
    '--cycles', type=int, default=None, help='Number of cycles the training should have')
train_parser.add_argument(
    '--unit-size', type=int, default=16, help='Environment grid size')
train_parser.add_argument(
    '--epsilon', type=float, default=0.01, help='Epsilon')
train_parser.set_defaults(func=train)


# Running
run_parser = subparsers.add_parser('run')
run_parser.add_argument(
    '--memory', type=str, help='Memory filename')
run_parser.add_argument(
    '--world', type=str, default=DEFAULT_WORLD, help='World filename')
run_parser.add_argument(
    '--speed', type=int, default=DEFAULT_SPEED, help='Environment speed')
run_parser.add_argument(
    '--unit-size', type=int, default=16, help='Environment grid size')
run_parser.add_argument(
    '--epsilon', type=float, default=0.01, help='Epsilon')
run_parser.set_defaults(func=run)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
