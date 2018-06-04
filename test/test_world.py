import unittest
from snake.world import World


class TestWorld(unittest.TestCase):
    def test_unit_to_pixel_convertion_default(self):
        world = World('data/worlds')
        self.assertEqual(world.to_px(16), 256)
