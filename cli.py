import argparse
import app

# Common
SPEED = 10
WORLD = 'default'
VIEW_SIZE = 16
VIEW_ENABLE = True
EPSILON = None

# Training defaults
CYCLES = None
EPISODES = 100
LEARN = 0.75
DISCOUNT = 0.9
REWARD = 'default'

parser = argparse.ArgumentParser(description='Q-learning Snake Game', add_help=False)

parser.add_argument('--memory', type=str, help='Memory filename')
parser.add_argument(
    '--speed', default=SPEED, type=int, help='Environment speed for visualization'
)
parser.add_argument('--world', default=WORLD, help='Environment world filename')
parser.add_argument(
    '--view-size',
    default=VIEW_SIZE,
    type=int,
    help='Size of environment world visualization',
)
parser.add_argument(
    '--view-enable',
    default=VIEW_ENABLE,
    type=bool,
    help='Enable/disable environment world visualization',
)
parser.add_argument(
    '--epsilon',
    default=EPSILON,
    help='aka. "ignore-the-policy" probability or a name function for it',
)
parser.add_argument('--cycles', default=CYCLES, type=int, help='Number of sessions')
parser.add_argument('--config', default=None, help='Configuration file for complex stuff')

parser.add_argument(
    '--episodes',
    #default=EPISODES,
    type=int,
    help='How many episodes a training session should train',
)
parser.add_argument(
    '--learn', default=LEARN, type=float, help='Agent learning ratio'
)
parser.add_argument(
    '--discount', default=DISCOUNT, type=float, help='Agent discount factor'
)
parser.add_argument('--reward', default=REWARD, help='Reward model name')

subparsers = parser.add_subparsers()

# Training
train_parser = subparsers.add_parser(
    'train', help='Train a agent to play the snake game', parents=[parser]
)
train_parser.set_defaults(func=app.handle, command='train')

# Run
run_parser = subparsers.add_parser(
    'run', help='Make a agent play in the environment without training', parents=[parser]
)
run_parser.set_defaults(func=app.handle, command='run')

if __name__ == '__main__':
    arg = parser.parse_args()
    arg.func(arg)
