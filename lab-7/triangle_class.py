# Импортируем функцию и исключение из предыдущего модуля
from triangle_func import get_triangle_type, IncorrectTriangleSides

# Класс, представляющий треугольник
class Triangle:
    def __init__(self, a, b, c):
        # Проверка на корректность сторон: ни одна не <= 0 и выполняется неравенство треугольника
        if any(s <= 0 for s in (a, b, c)) or a + b <= c or b + c <= a or a + c <= b:
            raise IncorrectTriangleSides("Invalid triangle sides")
        # Сохраняем стороны в свойствах объекта
        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        # Используем готовую функцию, чтобы определить тип
        return get_triangle_type(self.a, self.b, self.c)

    def perimeter(self):
        # Возвращаем сумму всех сторон
        return self.a + self.b + self.c
