from decimal import Decimal
import learning
import learning.memory
import snake


if __name__ == '__main__':

    ACTIONS = [-1, 0, 1]

    ADAPTER = learning.memory.DictMemoryStorageAdapter()
    MEMORY_TABLE = learning.memory.SingleMemoryTable(ADAPTER, ACTIONS)

    try:
        MEMORY_TABLE.load('memory.json')
    except FileNotFoundError:
        print('File not found.')

    AGENT = learning.Agent(Decimal(0.75), Decimal(0.9), MEMORY_TABLE)

    WORLD = snake.World('data/worlds', unit_size=32)
    WORLD.load('tiny')

    ENVIRONMENT = snake.Environment(AGENT, WORLD, speed=-1)

    try:
        ENVIRONMENT.train(1000000, 0.01, True)
    except KeyboardInterrupt:
        pass

    AGENT.save('memory.json')
