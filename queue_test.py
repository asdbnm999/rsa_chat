import tkinter as tk
from tkinter import font

# Создаем главное окно
root = tk.Tk()

# Устанавливаем шрифт
my_font = font.Font(family="Times New Roman")

# Получаем высоту строки
line_height = my_font.metrics("linespace")

print("Высота строки шрифта Times New Roman 12:", line_height, "пикселей")

# Закрываем окно
root.destroy()