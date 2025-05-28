# Импортируем pytest и наш класс + исключение
import pytest
from triangle_class import Triangle, IncorrectTriangleSides

# Позитивный тест: равносторонний треугольник
def test_equilateral():
    t = Triangle(3, 3, 3)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 9

# Позитивный тест: равнобедренный треугольник
def test_isosceles():
    t = Triangle(5, 5, 8)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 18

# Позитивный тест: разносторонний треугольник
def test_nonequilateral():
    t = Triangle(4, 5, 6)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 15

# Негативный тест: сторона равна 0
def test_invalid_zero():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 2, 3)

# Негативный тест: отрицательная сторона
def test_invalid_negative():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 2)

# Негативный тест: неравенство треугольника нарушено
def test_invalid_sum():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 3)
