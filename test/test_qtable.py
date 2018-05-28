import unittest
from core.environment import Action
from core.agent import QTable, Memory

class TestQTable(unittest.TestCase):
    def test_something(self):

        learning_rate = 0.5
        discount_factor = 0

        actions = [
            Action(10, 'Action A'),
            Action(20, 'Action B'),
            Action(30, 'Action C')
        ]

        table = QTable(actions)
        print('')
        table.update(Memory(2, actions[1], 100, 3), learning_rate, discount_factor)
        table.update(Memory(1, actions[0], 50, 2), learning_rate, discount_factor)

        # memory = Memory((0, 1), actions[0], 100, (0, 2))
        # table.update(memory, learning_rate, discount_factor)

        print(f'Q is: {table.get_q(1, actions[0])}' )        