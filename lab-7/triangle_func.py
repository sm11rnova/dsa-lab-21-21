# Определяем пользовательское исключение, если стороны треугольника некорректны
class IncorrectTriangleSides(Exception):
    pass

# Функция для определения типа треугольника по трём сторонам
def get_triangle_type(a, b, c):
    # Сортируем стороны по возрастанию, чтобы удобнее проверять неравенство треугольника
    sides = sorted([a, b, c])

    # Проверка: если есть сторона <= 0 или сумма двух наименьших <= третьей, то треугольник невозможен
    if any(s <= 0 for s in sides) or sides[0] + sides[1] <= sides[2]:
        raise IncorrectTriangleSides("Invalid triangle sides")

    # Все стороны равны
    if a == b == c:
        return "equilateral"
    # Две стороны равны
    elif a == b or b == c or a == c:
        return "isosceles"
    # Все стороны разные
    else:
        return "nonequilateral"