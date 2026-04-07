import math


def find_best_matrix_size(n):
    if n == 0:
        return 1, 1

    best_r, best_c = 1, n
    min_score = float('inf')

    for r in range(1, int(math.sqrt(n)) + 15):
        c = math.ceil(n / r)
        padding = r * c - n
        diff = abs(r - c)
        score = diff * 4 + padding

        if score < min_score:
            min_score = score
            best_r, best_c = r, c

    return best_r, best_c


def decrypt_transposition(ciphertext, rows=None, cols=None, pad_char='$'):
    n = len(ciphertext)

    print(f"Зашифрованный текст: {ciphertext}")
    print(f"Длина: {n}\n")

    # Определение размера матрицы
    if rows is None or cols is None:
        print("Введите размер матрицы (строки столбцы) через пробел, например: 4 3")
        print("Или нажмите Enter для автоматического выбора")

        user_input = input().strip()

        if user_input:
            try:
                parts = user_input.split()
                rows = int(parts[0])
                cols = int(parts[1])
                if rows <= 0 or cols <= 0:
                    raise ValueError
                print(f"Используется размер: {rows}×{cols}")
            except:
                print("Некорректный ввод → используется автоматический размер")
                rows, cols = find_best_matrix_size(n)
        else:
            rows, cols = find_best_matrix_size(n)
            print(f"Автоматически выбран размер: {rows}×{cols}")
    else:
        print(f"Используется заданный размер: {rows}×{cols}")

    # Проверка, что длина совпадает с размером матрицы
    matrix_size = rows * cols
    if n != matrix_size:
        print(f"Предупреждение: Длина текста ({n}) не равна размеру матрицы ({matrix_size})")
        # Можно дополнить или обрезать, но для дешифровки обычно должна совпадать

    # Создаём пустую матрицу
    matrix = [[' ' for _ in range(cols)] for _ in range(rows)]

    # Ввод ключей
    print("\nВведите ключ перестановки строк (через пробел):")
    row_key = list(map(int, input().strip().split()))

    print("Введите ключ перестановки столбцов (через пробел):")
    col_key = list(map(int, input().strip().split()))

    # Проверка длин ключей
    if len(row_key) != rows or len(col_key) != cols:
        print("Ошибка: Длина ключей не соответствует размерам матрицы!")
        return None

    # 1. Заполняем матрицу зашифрованным текстом по строкам
    idx = 0
    for i in range(rows):
        for j in range(cols):
            matrix[i][j] = ciphertext[idx]
            idx += 1

    print("\nМатрица после заполнения зашифрованным текстом:")
    for row in matrix:
        print('  '.join(row))

    # 2. Обратная перестановка столбцов (инверсия col_key)
    # Создаём обратный ключ для столбцов
    col_inv = [0] * cols
    for i, pos in enumerate(col_key):
        col_inv[pos - 1] = i + 1

    # Применяем обратную перестановку столбцов
    col_undone = []
    for row in matrix:
        new_row = [row[col_inv[j] - 1] for j in range(cols)]
        col_undone.append(new_row)

    print("\nПосле обратной перестановки столбцов:")
    for row in col_undone:
        print('  '.join(row))

    # 3. Обратная перестановка строк (инверсия row_key)
    row_inv = [0] * rows
    for i, pos in enumerate(row_key):
        row_inv[pos - 1] = i + 1

    # Применяем обратную перестановку строк
    plaintext_matrix = [col_undone[row_inv[i] - 1] for i in range(rows)]

    print("\nПосле обратной перестановки строк:")
    for row in plaintext_matrix:
        print('  '.join(row))

    # 4. Читаем результат по строкам
    plaintext = ''.join(''.join(row) for row in plaintext_matrix)

    # Убираем паддинг в конце (символы pad_char)
    plaintext = plaintext.rstrip(pad_char)

    print("\n" + "=" * 70)
    print("РАСШИФРОВАННЫЙ ТЕКСТ:")
    print(plaintext)

    return plaintext


# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    cipher = input("Введите зашифрованный текст: ").strip()

    if not cipher:
        cipher = "ПримерЗашифрованногоТекста"  # можно заменить на тестовый

    decrypt_transposition(cipher)