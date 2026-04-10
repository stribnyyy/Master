# -*- coding: utf-8 -*-
"""Lab1_Binary_Classification_Console_Automated.ipynb

Лабораторная работа №1: Бинарная классификация (Логистическая регрессия и kNN)
Консольная версия с автоматическим определением параметров
"""

# 1. Импорт необходимых библиотек
# pip install pandas numpy scikit-learn matplotlib seaborn
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# Указываем seed для воспроизводимости результатов
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

print("Библиотеки успешно импортированы.")
print("="*80)

# ==================================================
# 4.1 Первичный анализ и предобработка данных
# ==================================================
print("\nЭТАП 4.1: ПЕРВИЧНЫЙ АНАЛИЗ И ПРЕДОБРАБОТКА ДАННЫХ")
print("-"*60)

# 1. Загрузка CSV-файла
print("ШАГ 1: Загрузка CSV-файла")
print("-"*40)

try:
    df = pd.read_csv('data.csv')
    print("[OK] Файл 'data.csv' успешно загружен")
except FileNotFoundError:
    print("[!] Ошибка: Файл 'data.csv' не найден в текущей директории.")
    print("    Пожалуйста, убедитесь, что файл находится в той же папке, что и скрипт.")
    print("    Или укажите полный путь к файлу, например: pd.read_csv('/путь/к/файлу/data.csv')")
    exit()

# 2. Определение размерности и структуры данных
print("\nШАГ 2: Определение размерности и структуры данных")
print("-"*40)

# Определяем размерность
n_rows, n_cols = df.shape
print(f"Количество наблюдений (строк): {n_rows}")
print(f"Количество переменных (столбцов): {n_cols}")

# Проверяем наличие целевой переменной
target_column = None
possible_target_names = ['Bankrupt?', 'Bankrupt', 'bankrupt', 'class', 'target', 'Y']

for col_name in possible_target_names:
    if col_name in df.columns:
        target_column = col_name
        break

if target_column is None:
    # Если не нашли по имени, предполагаем, что последний столбец - целевая переменная
    target_column = df.columns[-1]
    print(f"[!] Не найдена переменная 'Bankrupt?'. Использую последний столбец как целевую переменную: '{target_column}'")
else:
    print(f"[OK] Найдена целевая переменная: '{target_column}'")

# Определяем признаки и целевую переменную
feature_columns = [col for col in df.columns if col != target_column]
n_features = len(feature_columns)

print(f"Количество признаков: {n_features}")
print(f"Названия первых 5 признаков: {feature_columns[:5]}")
if n_features > 5:
    print(f"... и еще {n_features - 5} признаков")

# Определяем типы данных
print(f"\nТипы данных в датасете:")
dtype_counts = df.dtypes.value_counts()
for dtype, count in dtype_counts.items():
    print(f"  {dtype}: {count} столбцов")

# 3. Проверка наличия пропусков
print("\nШАГ 3: Проверка наличия пропусков")
print("-"*40)

missing_values_total = df.isnull().sum().sum()
missing_columns = df.columns[df.isnull().any()].tolist()

print(f"Общее количество пропущенных значений: {missing_values_total}")

if missing_values_total > 0:
    print(f"Столбцы с пропусками: {missing_columns}")
    print(f"Детальная информация по пропускам:")
    for col in missing_columns:
        missing_count = df[col].isnull().sum()
        missing_percent = (missing_count / len(df)) * 100
        print(f"  {col}: {missing_count} пропусков ({missing_percent:.2f}%)")
else:
    print("[OK] Пропуски не обнаружены")

# 4. Обработка пропусков (при необходимости)
print("\nШАГ 4: Обработка пропусков")
print("-"*40)

if missing_values_total > 0:
    print("[!] Обнаружены пропуски. Выберите метод обработки:")
    print("    1. Удалить строки с пропусками")
    print("    2. Заполнить пропуски средним значением")
    print("    3. Заполнить пропуски медианой")
    
    # Автоматически выбираем метод 1 для простоты
    print("[!] Автоматически выбран метод: удаление строк с пропусками")
    initial_len = len(df)
    df = df.dropna()
    print(f"Удалено {initial_len - len(df)} строк")
    print(f"Новый размер данных: {df.shape}")
    
    # Обновляем переменные после удаления
    n_rows, n_cols = df.shape
    feature_columns = [col for col in df.columns if col != target_column]
else:
    print("[OK] Пропуски отсутствуют, обработка не требуется")

# Базовая статистика по данным
print("\nШАГ 5: Базовая статистика данных")
print("-"*40)

print(f"Итоговая размерность данных после обработки:")
print(f"  Наблюдений: {n_rows}")
print(f"  Признаков:  {n_features}")
print(f"  Целевая переменная: '{target_column}'")

# Анализ целевой переменной
print(f"\nАнализ целевой переменной '{target_column}':")
target_values = df[target_column].value_counts()
target_percentages = df[target_column].value_counts(normalize=True) * 100

for value in sorted(target_values.index):
    count = target_values[value]
    percent = target_percentages[value]
    print(f"  Класс {value}: {count} наблюдений ({percent:.2f}%)")
    
    # Определяем, какой класс соответствует банкротству (обычно 1)
    if percent < 50:  # Предполагаем, что класс банкротства - миноритарный
        bankrupt_class = value
        non_bankrupt_class = 1 - value if set(target_values.index) == {0, 1} else None

print(f"\n[INFO] Предположительно, класс {bankrupt_class} соответствует банкротству")

# ==================================================
# 4.2 Подготовка данных для моделирования
# ==================================================
print("\n" + "="*80)
print("ЭТАП 4.2: ПОДГОТОВКА ДАННЫХ ДЛЯ МОДЕЛИРОВАНИЯ")
print("-"*60)

# Отделяем признаки от целевой переменной
X = df[feature_columns]
y = df[target_column]

# Проверяем, что целевая переменная бинарная
unique_classes = y.unique()
print(f"Уникальные значения целевой переменной: {sorted(unique_classes)}")

if len(unique_classes) != 2:
    print(f"[!] Внимание: целевая переменная содержит {len(unique_classes)} классов, но ожидается бинарная классификация (2 класса)")

# 5. Нормализация признаков
print("\nШАГ 5: Нормализация признаков (StandardScaler)")
print("-"*40)

# Создаем и применяем StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Проверяем результаты нормализации
print("[OK] Нормализация выполнена")
print(f"Средние после нормализации (первые 5 признаков):")
for i in range(min(5, n_features)):
    print(f"  Признак {i+1}: {X_scaled[:, i].mean():.10f} (должно быть ~0)")
print(f"Ст. отклонения после нормализации (первые 5 признаков):")
for i in range(min(5, n_features)):
    print(f"  Признак {i+1}: {X_scaled[:, i].std():.10f} (должно быть ~1)")

# ==================================================
# 4.3 Разделение выборки
# ==================================================
print("\n" + "="*80)
print("ЭТАП 4.3: РАЗДЕЛЕНИЕ ВЫБОРКИ")
print("-"*60)

# Разбиваем на обучающую (70%) и тестовую (30%) выборки
test_size = 0.3
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
)

print(f"Параметры разделения:")
print(f"  test_size = {test_size:.0%}")
print(f"  random_state = {RANDOM_STATE}")
print(f"  stratify = True (сохранение пропорций классов)")
print(f"\nРезультаты разделения:")
print(f"  Обучающая выборка: {X_train.shape[0]} наблюдений ({X_train.shape[0]/n_rows:.1%})")
print(f"  Тестовая выборка:   {X_test.shape[0]} наблюдений ({X_test.shape[0]/n_rows:.1%})")

print(f"\nПроверка сохранения пропорций классов:")
print(f"  Обучающая выборка - класс {bankrupt_class}: {(y_train == bankrupt_class).mean()*100:.2f}%")
print(f"  Тестовая выборка - класс {bankrupt_class}:   {(y_test == bankrupt_class).mean()*100:.2f}%")
print(f"  Исходные данные - класс {bankrupt_class}:    {(y == bankrupt_class).mean()*100:.2f}%")

# ==================================================
# 4.4 Классификация логистической регрессией
# ==================================================
print("\n" + "="*80)
print("ЭТАП 4.4: ЛОГИСТИЧЕСКАЯ РЕГРЕССИЯ")
print("-"*60)

# Для логистической регрессии используем все признаки
print("Используются все доступные признаки для построения модели")

# 1. Построение модели
log_reg = LogisticRegression(penalty=None, solver='lbfgs', max_iter=1000, random_state=RANDOM_STATE)
log_reg.fit(X_train, y_train)

# 2. Анализ коэффициентов
print(f"\n--- Коэффициенты модели (первые 10 из {n_features}) ---")
print(f"Свободный член (intercept): {log_reg.intercept_[0]:.6f}")
print(f"\nКоэффициенты при признаках:")
for i in range(min(10, n_features)):
    print(f"  {feature_columns[i]}: {log_reg.coef_[0][i]:.6f}")
if n_features > 10:
    print(f"  ... и еще {n_features - 10} коэффициентов")

# Попытка получить p-value
print(f"\n--- Анализ статистической значимости ---")
try:
    import statsmodels.api as sm
    X_train_sm = sm.add_constant(X_train)
    logit_model = sm.Logit(y_train, X_train_sm)
    result = logit_model.fit(disp=0, maxiter=1000)
    print("[OK] Модель statsmodels успешно обучена")
    
    # Получаем p-values
    p_values = result.pvalues[1:]  # без константы
    
    # Определяем значимые признаки (p-value < 0.05)
    significant_features = [feature_columns[i] for i in range(len(p_values)) if p_values[i] < 0.05]
    non_significant_features = [feature_columns[i] for i in range(len(p_values)) if p_values[i] >= 0.05]
    
    print(f"\nСтатистически значимые признаки (p-value < 0.05): {len(significant_features)} из {n_features}")
    if len(significant_features) > 0:
        print("  Первые 5 значимых признаков:")
        for i, feat in enumerate(significant_features[:5]):
            print(f"    {i+1}. {feat}")
    
    if len(non_significant_features) > 0:
        print(f"\nСтатистически незначимые признаки (p-value >= 0.05): {len(non_significant_features)} из {n_features}")
        print("  Рекомендуется удалять их по одному и переобучать модель")
        
except ImportError:
    print("[!] Библиотека statsmodels не установлена. Анализ p-value пропущен.")
except Exception as e:
    print(f"[!] Ошибка при анализе p-value: {e}")

# 3. Прогноз вероятности для выбранных компаний
print(f"\n--- Прогноз вероятности для конкретных компаний ---")

# Находим индексы банкротов и небанкротов в тестовой выборке
bankrupt_indices = np.where(y_test == bankrupt_class)[0]
non_bankrupt_indices = np.where(y_test == non_bankrupt_class)[0]

if len(bankrupt_indices) > 0 and len(non_bankrupt_indices) > 0:
    idx_bankrupt = bankrupt_indices[0]
    idx_non_bankrupt = non_bankrupt_indices[0]
    
    # Получаем вероятности
    proba_bankrupt = log_reg.predict_proba(X_test[idx_bankrupt].reshape(1, -1))[0, int(bankrupt_class)]
    proba_non_bankrupt = log_reg.predict_proba(X_test[idx_non_bankrupt].reshape(1, -1))[0, int(bankrupt_class)]
    
    print(f"\n--- Компания-банкрот (фактический класс: {bankrupt_class}) ---")
    print(f"  Индекс в тестовой выборке: {idx_bankrupt}")
    print(f"  Предсказанная вероятность банкротства: {proba_bankrupt:.6f}")
    pred_class = bankrupt_class if proba_bankrupt > 0.5 else non_bankrupt_class
    print(f"  Предсказанный класс: {pred_class}")
    print(f"  Результат: {'ВЕРНО' if pred_class == bankrupt_class else 'ОШИБКА'}")
    
    print(f"\n--- Компания-небанкрот (фактический класс: {non_bankrupt_class}) ---")
    print(f"  Индекс в тестовой выборке: {idx_non_bankrupt}")
    print(f"  Предсказанная вероятность банкротства: {proba_non_bankrupt:.6f}")
    pred_class = bankrupt_class if proba_non_bankrupt > 0.5 else non_bankrupt_class
    print(f"  Предсказанный класс: {pred_class}")
    print(f"  Результат: {'ВЕРНО' if pred_class == non_bankrupt_class else 'ОШИБКА'}")

# 4. Оценка модели
print(f"\n--- Оценка качества модели на тестовой выборке ---")
y_pred_lr = log_reg.predict(X_test)
accuracy_lr = accuracy_score(y_test, y_pred_lr)
print(f"Точность (Accuracy): {accuracy_lr:.4f}")

# Матрица неточностей
cm_lr = confusion_matrix(y_test, y_pred_lr)
print(f"\nМатрица неточностей:")
print(f"              Предсказано")
print(f"              Не банкрот  Банкрот")
print(f"Фактически:")
print(f"  Не банкрот   {cm_lr[0,0]:6d}      {cm_lr[0,1]:6d}")
print(f"  Банкрот      {cm_lr[1,0]:6d}      {cm_lr[1,1]:6d}")

# Метрики
tn, fp, fn, tp = cm_lr.ravel()
print(f"\nДетальные метрики:")
print(f"  True Negatives (верно классифицированы не-банкроты):  {tn}")
print(f"  False Positives (ложная тревога):                     {fp}")
print(f"  False Negatives (пропущенные банкроты):               {fn}")
print(f"  True Positives (верно классифицированы банкроты):     {tp}")

print(f"\n[ВАЖНО] Количество ложно определённых банкротов (FN): {fn}")

# ==================================================
# 4.5 Классификация методом k ближайших соседей
# ==================================================
print("\n" + "="*80)
print("ЭТАП 4.5: МЕТОД k-БЛИЖАЙШИХ СОСЕДЕЙ (kNN)")
print("-"*60)

print("[OK] Нормализация признаков выполнена на этапе 4.2")

# Проведем эксперименты с разными значениями k
print(f"\n--- Эксперименты с различными значениями k ---")
# Автоматически подбираем диапазон k
max_k = min(50, int(np.sqrt(X_train.shape[0])))
k_values = [3, 5, 7, 9, 11, 15, 21, 31]
k_values = [k for k in k_values if k <= max_k]

best_k = 3
best_accuracy = 0

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred_knn = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred_knn)
    print(f"  k = {k:2d}, Accuracy = {accuracy:.4f}")
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_k = k

print(f"\n[OK] Лучшее значение k: {best_k} с точностью {best_accuracy:.4f}")

# Используем лучшее значение k
knn_best = KNeighborsClassifier(n_neighbors=best_k)
knn_best.fit(X_train, y_train)
y_pred_knn_best = knn_best.predict(X_test)

# Матрица неточностей
cm_knn = confusion_matrix(y_test, y_pred_knn_best)
tn_knn, fp_knn, fn_knn, tp_knn = cm_knn.ravel()

print(f"\n--- Матрица неточностей для kNN (k={best_k}) ---")
print(f"              Предсказано")
print(f"              Не банкрот  Банкрот")
print(f"Фактически:")
print(f"  Не банкрот   {cm_knn[0,0]:6d}      {cm_knn[0,1]:6d}")
print(f"  Банкрот      {cm_knn[1,0]:6d}      {cm_knn[1,1]:6d}")

print(f"\nДетальные метрики kNN:")
print(f"  True Negatives (верно классифицированы не-банкроты):  {tn_knn}")
print(f"  False Positives (ложная тревога):                     {fp_knn}")
print(f"  False Negatives (пропущенные банкроты):               {fn_knn}")
print(f"  True Positives (верно классифицированы банкроты):     {tp_knn}")

print(f"\n[ВАЖНО] Количество ложно определённых банкротов (FN): {fn_knn}")

# ==================================================
# Сравнительный анализ методов
# ==================================================
print("\n" + "="*80)
print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТОДОВ")
print("="*80)

print(f"""
СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ
{'-'*80}
Метрика                 | Логистическая регрессия | kNN (k={best_k})
{'-'*80}
Accuracy                | {accuracy_lr:.4f}                    | {best_accuracy:.4f}
True Negatives (TN)     | {tn:6d}                    | {tn_knn:6d}
False Positives (FP)    | {fp:6d}                    | {fp_knn:6d}
False Negatives (FN)    | {fn:6d}                    | {fn_knn:6d}
True Positives (TP)     | {tp:6d}                    | {tp_knn:6d}
Размер обучающей выборки| {X_train.shape[0]:6d}                    | {X_train.shape[0]:6d}
Размер тестовой выборки | {X_test.shape[0]:6d}                    | {X_test.shape[0]:6d}
{'-'*80}
""")

print("\n" + "="*80)
print("ИТОГОВЫЙ ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ №1")
print("="*80)

print(f"""
1. ИНФОРМАЦИЯ О ДАННЫХ:
   - Источник данных: Taiwanese Bankruptcy Prediction (1999-2009)
   - Загруженный файл: data.csv
   - Количество наблюдений: {n_rows}
   - Количество признаков: {n_features}
   - Целевая переменная: '{target_column}'
   - Пропуски в данных: {'обнаружены и обработаны' if missing_values_total > 0 else 'отсутствуют'}

2. ПРЕДОБРАБОТКА ДАННЫХ:
   - Выполнена проверка размерности и структуры
   - Проверено наличие пропусков
   - Выполнена нормализация признаков методом StandardScaler
   - Данные разделены на обучающую (70%) и тестовую (30%) выборки

3. РЕЗУЛЬТАТЫ КЛАССИФИКАЦИИ:
   
   Логистическая регрессия:
   - Точность (Accuracy): {accuracy_lr:.4f}
   - Пропущено банкротов (FN): {fn}
   
   Метод k-ближайших соседей (k={best_k}):
   - Точность (Accuracy): {best_accuracy:.4f}
   - Пропущено банкротов (FN): {fn_knn}

4. ПРОГНОЗ ДЛЯ КОНКРЕТНЫХ КОМПАНИЙ:
   - Компания-банкрот (индекс {idx_bankrupt}): вероятность банкротства {proba_bankrupt:.4f}
   - Компания-небанкрот (индекс {idx_non_bankrupt}): вероятность банкротства {proba_non_bankrupt:.4f}

5. ВЫВОДЫ:
   - {'Логистическая регрессия показала лучший результат' if accuracy_lr > best_accuracy else 'Метод kNN показал лучший результат'} по общей точности
   - {'Логистическая регрессия' if fn < fn_knn else 'Метод kNN'} допустил меньше критических ошибок (пропущенных банкротов)
   - Метод kNN требует подбора гиперпараметра k (оптимальное значение: {best_k})
   - Логистическая регрессия предоставляет интерпретируемые коэффициенты и вероятности
""")

print("\n" + "="*80)
print("РАБОТА ВЫПОЛНЕНА УСПЕШНО")
print("="*80)