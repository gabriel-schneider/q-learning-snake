import learning
import snake
import datetime
import os
import statistics
import csv
from decimal import Decimal
import epsilon

ACTIONS = [-1, 0, 1]


def export_results(cycle, results, filename):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        if file.tell() == 0:
            writer.writerow(['cycle', 'steps', 'score', 'wins', 'loses', 'starves'])
        writer.writerow(
            [
                cycle,
                statistics.mean(results.steps),
                statistics.mean(results.scores),
                results.wins,
                results.loses,
                results.starves,
            ]
        )
        file.close()


def generate_memory_filename():
    """Return a formated memory filename."""
    return f'memory_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'


def load_memory(memory_table, filename):
    try:
        if memory_table.load(filename):
            print(f'File {filename} loaded with success!')
            return filename
    except Exception:
        pass

    new_filename = generate_memory_filename()
    print(f'Creating a new memory file: {new_filename}!')
    return new_filename




def handle(arguments):

    adapter = learning.memory.DictMemoryStorageAdapter()
    memory_table = learning.memory.SingleMemoryTable(adapter, ACTIONS)

    arguments.memory = load_memory(memory_table, arguments.memory)

    agent = learning.Agent(
        Decimal(arguments.learn), Decimal(arguments.discount), memory_table
    )
    world = snake.environment.World('data/worlds', arguments.view_size)

    world.load(arguments.world)

    reward_model = snake.rewards.create(arguments.reward)
    environment = snake.Environment(agent, world, arguments.speed, reward_model)

    # Create a directory for statistics files
    stats_directory = f'data/stats/{arguments.memory}'
    if not os.path.exists(stats_directory):
        os.makedirs(stats_directory)

    cycles_left = arguments.cycles

    try:
        while cycles_left > 0 or arguments.cycles <= 0:

            cycles_current = arguments.cycles - cycles_left
            if arguments.epsilon is None:
                arguments.epsilon = epsilon.default
            elif isinstance(arguments.epsilon, str):
                arguments.epsilon = getattr(epsilon, arguments.epsilon, epsilon.default)

            training = arguments.command == 'train'
            results = environment.execute(training, arguments.episodes, arguments.epsilon, [cycles_current, arguments.cycles, environment], arguments.view_enable)
            
            if results.abort:
                break

            export_results(
                cycles_current,
                results,
                f'{stats_directory}/results.csv',
            )
            cycles_left -= 1
    except KeyboardInterrupt:
        pass
