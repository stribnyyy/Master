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


def generate_default_key(length):
    if length <= 1:
        return [1]

    key = list(range(1, length + 1))
    if length >= 2:
        key[0], key[1] = key[1], key[0]
    if length >= 4:
        key[2], key[3] = key[3], key[2]
    if length >= 5:
        key[1], key[4] = key[4], key[1]
    return key


def encrypt_transposition(plaintext, pad_char='$'):
    n = len(plaintext)

    print(f"Исходный текст: {plaintext}")
    print(f"Длина текста: {n}\n")

    print("Хотите задать размер матрицы вручную?")
    print("Введите два числа через пробел (строки столбцы), например: 4 3")
    print("Или просто нажмите Enter для автоматического выбора")

    user_input = input().strip()

    if user_input:
        try:
            parts = user_input.split()
            rows = int(parts[0])
            cols = int(parts[1])
            if rows <= 0 or cols <= 0:
                raise ValueError
            print(f"Вы выбрали размер матрицы: {rows}×{cols}")
        except:
            print("Некорректный ввод! Используется автоматический размер.")
            rows, cols = find_best_matrix_size(n)
    else:
        rows, cols = find_best_matrix_size(n)
        print(f"Автоматически выбран размер матрицы: {rows}×{cols}")

    padding = rows * cols - n
    padded = plaintext + pad_char * padding

    print(f"После дополнения: {padded} (добавлено {padding} символов '{pad_char}')\n")

    matrix = [list(padded[i * cols:(i + 1) * cols]) for i in range(rows)]

    print("Исходная матрица:")
    for row in matrix:
        print('  '.join(row))

    row_key = generate_default_key(rows)
    col_key = generate_default_key(cols)

    print(f"\nКлюч перестановки строк:  {row_key}")
    print(f"Ключ перестановки столбцов: {col_key}\n")

    row_permuted = [matrix[k - 1] for k in row_key]

    print("После перестановки строк:")
    for row in row_permuted:
        print('  '.join(row))

    col_permuted = [[row[k - 1] for k in col_key] for row in row_permuted]

    print("\nПосле перестановки столбцов:")
    for row in col_permuted:
        print('  '.join(row))

    ciphertext = ''.join(''.join(row) for row in col_permuted)

    print("\n" + "=" * 70)
    print("ЗАШИФРОВАННЫЙ ТЕКСТ:")
    print(ciphertext)

    return ciphertext


text = input("Введите текст для шифрования: ").strip()

if not text:
    text = "КРИПТОГРАФИЯ"

encrypt_transposition(text, pad_char='$')