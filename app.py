import json
import datetime
import os
import statistics
import csv
from decimal import Decimal
import epsilons
import learning
import snake
import random


ACTIONS = [-1, 0, 1]

class AbortException(Exception):
    pass

def export_results(headers, data, filename):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        if file.tell() == 0:
            writer.writerow(headers)
        writer.writerow(data)
    return True

def export_world_results(cycle, results, filename):
    data = [
        cycle,
        statistics.mean(results.steps),
        statistics.mean(results.scores),
        results.wins,
        results.loses,
        results.starves
    ]
    return export_results(['cycle', 'steps', 'score', 'wins', 'loses', 'starves'], data, filename)

def export_cycle_results(cycle, results, filename):
    data = [
        cycle,
        statistics.mean((statistics.mean(r.steps) for r in results)),
        statistics.mean((statistics.mean(r.scores) for r in results)),
        statistics.mean((r.wins for r in results)),
        statistics.mean((r.loses for r in results)),
        statistics.mean((r.starves for r in results))
    ]
    return export_results(['cycle', 'steps', 'score', 'wins', 'loses', 'starves'], data, filename)

def generate_memory_filename():
    """Return a random memory filename."""
    with open('data/names.txt', 'r') as file:
        names = file.read().splitlines()
        random.shuffle(names)

    #return f'memory_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
    return ''.join([x.capitalize() for x in names[:4]])


def load_memory(memory_table, filename):
    try:
        if memory_table.load(filename):
            print(f'File {filename} loaded with success!')
            return True
    except Exception:
        pass
    return False

def _setup_config(arguments):
    config = {}
    if arguments.config:
        filename = f'data/configurations/{arguments.config}'
        file = open(filename, 'r')
        try:
            config = json.load(file)
            print(f'Configuration File: {filename}')
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(e)

    if 'name' in config:
        print(f">> {config['name']}")

    if 'memory_table' in config:
        print('Importing memory table configuration data...')
        if 'adapters' in config['memory_table']:
            adapters = []
            for adapter in config['memory_table']['adapters']:
                adapters.append(learning.memory.create_adapter(adapter['name'], adapter['args']))
        else:
            adapters = [learning.memory.create_adapter('dict')]

        args = adapters + config['memory_table']['args']
        memory_table = learning.memory.create_memory_table(config['memory_table']['name'], ACTIONS, args)
    else:
        adapter = learning.memory.DictMemoryStorageAdapter()
        memory_table = learning.memory.SingleMemoryTable(ACTIONS, adapter)

    if arguments.command == 'train':
        learn = arguments.learn
        discount = arguments.discount

        if 'agent' in config:
            print('Importing agent configuration data...')
            if 'learning' in config['agent']:
                learn = config['agent']['learning']
            if 'discount' not in config['agent']:
                discount = config['agent']['discount']
    else:
        learn = 0
        discount = 0

    if arguments.command == 'train':
        reward_model = snake.rewards.create(arguments.reward)
        if 'environment' in config:
            print('Importing environment configuration data...')
            if 'reward_model' in config['environment']:
                print('Importing reward model configuration data...')
                reward_model = snake.rewards.create(config['environment']['reward_model'])
    else:
        print('Using default reward model...')
        reward_model = None


    # Create the worlds list
    worlds = [{
        'name': arguments.world,
        'episodes': arguments.episodes if arguments.episodes else 100
    }]

    # Setup worlds list
    if 'worlds' in config:
        print('Importing worlds configuration data...')
        worlds.clear()
        for world in config['worlds']:
            name = world['name']
            if 'episodes' in world:
                episodes = world['episodes'] if not arguments.episodes else arguments.episodes
            else:
                episodes = arguments.episodes if arguments.episodes else 100

            worlds.append({
                'name': name,
                'episodes': episodes
            })
    
    # Setup cycles
    if arguments.cycles:
        cycles = arguments.cycles
    elif 'cycles' in config:
        cycles = config['cycles']
    else:
        cycles = 1

    if arguments.epsilon is None:
        print('Using default epsilon function...')
        epsilon = epsilons.default
    elif isinstance(arguments.epsilon, str):
        try:
            epsilon = float(arguments.epsilon)
        except ValueError:
            epsilon = getattr(epsilons, arguments.epsilon, epsilons.default)

    agent = learning.Agent(Decimal(learn), Decimal(discount), memory_table)
    world = snake.environment.World('data/worlds', arguments.view_size)
    environment = snake.Environment(agent, world, arguments.speed, reward_model)

    return (cycles, epsilon, environment, worlds)


def handle(arguments):

    cycles_max, epsilon, environment, worlds = _setup_config(arguments)

    memory_filename = f'data/memories/{arguments.memory}'
    if arguments.memory:
        if load_memory(environment.agent.memories, memory_filename):
            print(f'Memory "{arguments.memory}" imported with success!')
    else:
        arguments.memory = generate_memory_filename()
        memory_filename = f'data/memories/{arguments.memory}'
        print(f'Generating file "{arguments.memory}" as memory!')

    if not arguments.no_stats:
        if arguments.stats_dir:
            stats_directory = f'data/statistics/{arguments.stats_dir}'
        else:
            stats_directory = f'data/statistics/{arguments.memory}/{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        print(f'Statistics will be saved at: {stats_directory}')

        if not os.path.exists(stats_directory):
            os.makedirs(stats_directory)
    else:
        print("Statistics output are disabled!")

    cycles_left = cycles_max
    try:
        while cycles_left > 0 or cycles_max <= 0:

            cycles_current = cycles_max - cycles_left
            worlds_results = []
            print(f'[Cycle {cycles_current + 1} of {cycles_max}]')
            try:
                for world in worlds:
                    print(f'Executing world "{world["name"]}" for {world["episodes"]} episodes...')
                    environment.world.load(world['name'])
                    results = environment.execute(arguments.command == 'train', world['episodes'], epsilon, [cycles_current, cycles_max, environment], arguments.view_enable)                   
                    if results.abort:
                        raise AbortException

                    if not arguments.no_stats:
                        export_world_results(cycles_current, results, f'{stats_directory}/{world["name"]}.csv')
                    worlds_results.append(results)
            except AbortException:
                break
            if not arguments.no_stats:
                export_cycle_results(cycles_current, worlds_results, f'{stats_directory}/results.csv')
            cycles_left -= 1
    except KeyboardInterrupt:
        pass

    if arguments.command == 'train':
        print(f'Saving at "{memory_filename}"...' )
        environment.agent.save(memory_filename)
