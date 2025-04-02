# [Лабораторная работа 1] Задание 3.6
# Вариант 6

import sys

# Считываем массив из аргументов командной строки
arr = list(map(int, sys.argv[1:]))

if not arr:
    print("Массив пуст.")
    sys.exit()

# 1. Найти максимальный элемент
max_num = arr[0]
for num in arr:
    if num > max_num:
        max_num = num

print("Максимальный элемент:", max_num)

# 2. Количество чисел меньше максимального
count_less = 0
for num in arr:
    if num < max_num:
        count_less += 1

print("Количество чисел меньше максимального:", count_less)

# 3. Сумма чисел больше 5
sum_gt5 = 0
for num in arr:
    if num > 5:
        sum_gt5 += num

print("Сумма чисел больше 5:", sum_gt5)