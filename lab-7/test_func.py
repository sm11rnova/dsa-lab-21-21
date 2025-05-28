# Импорт стандартного фреймворка для тестирования
import unittest
# Импортируем функцию и исключение для тестирования
from triangle_func import get_triangle_type, IncorrectTriangleSides

# Класс тестов, унаследованный от unittest.TestCase
class TestGetTriangleType(unittest.TestCase):
    def test_equilateral(self):
        # Проверка равностороннего треугольника
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")

    def test_isosceles(self):
        # Проверка равнобедренного треугольника
        self.assertEqual(get_triangle_type(5, 5, 8), "isosceles")

    def test_nonequilateral(self):
        # Проверка разностороннего треугольника
        self.assertEqual(get_triangle_type(4, 5, 6), "nonequilateral")

    def test_invalid_zero(self):
        # Проверка: одна сторона — 0, должно быть исключение
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 2, 3)

    def test_invalid_negative(self):
        # Проверка: одна сторона отрицательная
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 2)

    def test_invalid_sum(self):
        # Проверка: сумма двух сторон равна третьей — не треугольник
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)