# [Лабораторная работа 1] Задание 2.6
# Вариант 6

text = input("Введите строку: ")

count = 0
new_text = ""

for char in text:
    if char != "a":
        new_text += char
    else:
        count += 1

print("Изменённая строка:", new_text)
print("Удалено символов 'a':", count)