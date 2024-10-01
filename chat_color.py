import random

def generate_hex_color():
    """Генерирует один случайный шестнадцатиричный цвет в формате #XXXXXX."""
    while True:
        r = random.randint(0, 255)  # Красный
        g = random.randint(0, 255)  # Зеленый
        b = random.randint(0, 255)  # Синий
        hex_color = f'#{r:02x}{g:02x}{b:02x}'

        # Проверяем, чтобы цвет не был фиолетовым
        if not (r < 100 and b > 100):  # Условие для исключения фиолетового
            # Преобразуем в шестнадцатиричный формат
            hex_color = f'#{r:02X}{g:02X}{b:02X}'
            return hex_color

