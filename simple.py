from decimal import Decimal
import learning
import learning.memory
import snake
import statistics
import csv
import random

if __name__ == '__main__':

    ACTIONS = [-1, 0, 1]

    # Single
    ADAPTER = learning.memory.DictMemoryStorageAdapter()
    MEMORY_TABLE = learning.memory.SingleMemoryTable(ADAPTER, ACTIONS)

    # Double
    # ADAPTER = learning.memory.DictMemoryStorageAdapter()
    # HIDDEN_ADAPTER = learning.memory.DictMemoryStorageAdapter()
    # MEMORY_TABLE = learning.memory.DoubleMemoryTable(
    #     ADAPTER, HIDDEN_ADAPTER, ACTIONS, 5000)

    try:
        MEMORY_TABLE.load('memory.json')
    except FileNotFoundError:
        print('File not found.')

    AGENT = learning.Agent(Decimal(0.75), Decimal(0.9), MEMORY_TABLE)

    WORLD = snake.World('data/worlds', unit_size=32)
    WORLD.load('tiny')

    REWARD_MODEL = snake.rewards.DistanceReward()
    ENVIRONMENT = snake.Environment(
        AGENT, WORLD, speed=-1, reward=REWARD_MODEL)

    random.seed()

    def epsilon(value):
        """Return epsilon for a cycle."""
        return 0.01 - (0.00985 * min(value, 75) / 75)

    for cycle in range(1, 100):
        try:
            RESULTS = ENVIRONMENT.train(
                100, epsilon(cycle), True)
            if RESULTS.abort:
                break
            print(RESULTS)
            with open('statistics.csv', 'a', newline='') as file:
                WRITER = csv.writer(file, delimiter=';')
                if file.tell() == 0:
                    WRITER.writerow(
                        ['cycle', 'steps', 'score', 'wins', 'loses', 'starves'])
                WRITER.writerow([cycle, statistics.mean(
                    RESULTS.steps), statistics.mean(RESULTS.scores), RESULTS.wins, RESULTS.loses, RESULTS.starves])
                file.close()
        except KeyboardInterrupt:
            break

    AGENT.save('memory.json')
