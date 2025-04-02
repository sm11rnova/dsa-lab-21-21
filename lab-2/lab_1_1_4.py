# 4. Последовательность чисел, сумма и количество (цикл while)
print("Введите целые числа (для окончания введите q):")
s = 0
count = 0
while True:
    val = input()
    if val == 'q':
        break
    s += int(val)
    count += 1

print("Сумма:", s)
print("Количество:", count)