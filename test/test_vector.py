import unittest
import math
from snake import Vector


class TestVector(unittest.TestCase):
    def test_rotation(self):
        vec = Vector(1, 0)
        vectors = [Vector(1, 0), Vector(1, 1), Vector(
            0, 1), Vector(-1, 1), Vector(-1, 0), Vector(-1, -1), Vector(0, -1), Vector(1, -1)]
        for i in range(8):
            self.assertEqual(vec, vectors[i])
            vec = vec.rotated(math.radians(45))

    def test_distance_horizontal_zero_to_ten(self):
        vector_a = Vector(0, 0)
        vector_b = Vector(10, 0)

        distance = vector_a.distance(vector_b)
        self.assertEqual(distance, 10)

    def test_distance_horizontal_five_to_nine(self):
        vector_a = Vector(5, 0)
        vector_b = Vector(9, 0)

        distance = vector_a.distance(vector_b)
        self.assertEqual(distance, 4)

    def test_distance_vertical_zero_to_six(self):
        vector_a = Vector(0, 0)
        vector_b = Vector(0, 6)

        distance = vector_a.distance(vector_b)
        self.assertEqual(distance, 6)

    def test_distance_vertical_three_to_eight(self):
        vector_a = Vector(0, 3)
        vector_b = Vector(0, 8)

        distance = vector_a.distance(vector_b)
        self.assertEqual(distance, 5)

    def test_distance_same_points(self):
        vector_a = Vector(2, 2)
        vector_b = Vector(2, 2)

        distance = vector_a.distance(vector_b)
        self.assertEqual(distance, 0)

    def test_distance_diagonal_origin(self):
        vector_a = Vector(0, 0)
        vector_b = Vector(2, 2)

        distance = vector_a.distance(vector_b)
        self.assertAlmostEqual(distance, 2.828427, delta=0.001)

    def test_distance_diagonal_main(self):
        vector_a = Vector(2, 3)
        vector_b = Vector(5, 7)

        distance = vector_a.distance(vector_b)
        self.assertAlmostEqual(distance, 5)

    def test_distance_diagonal_anti(self):
        vector_a = Vector(7, 3)
        vector_b = Vector(1, 2)

        distance = vector_a.distance(vector_b)
        self.assertAlmostEqual(distance, 6.082763, delta=0.001)
