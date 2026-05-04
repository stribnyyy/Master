# -*- coding: utf-8 -*-
"""
Лабораторная работа №6
Установление авторства текста методами машинного обучения
"""

import os
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ------------------------------------------------------------
# 1. Загрузка текстов из папок
# ------------------------------------------------------------
def load_texts_from_folder(folder_path, label=None):
    texts = []
    labels = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    texts.append(text)
                    if label is not None:
                        labels.append(label)
            except UnicodeDecodeError:
                # Если файл не в utf-8, пробуем cp1251
                with open(filepath, 'r', encoding='cp1251') as f:
                    text = f.read()
                    texts.append(text)
                    if label is not None:
                        labels.append(label)
    return texts, labels

# Укажите путь к папке authors
BASE_DIR = "authors"  # измените, если папка находится в другом месте

# Собираем всех авторов (все папки, кроме blok_a_a)
all_authors = [d for d in os.listdir(BASE_DIR)
               if os.path.isdir(os.path.join(BASE_DIR, d)) and d != 'blok_a_a']

print(f"Найдены авторы: {all_authors}")

all_texts = []
all_labels = []

for author in all_authors:
    folder = os.path.join(BASE_DIR, author)
    texts, _ = load_texts_from_folder(folder, label=author)
    all_texts.extend(texts)
    all_labels.extend([author] * len(texts))
    print(f"{author}: {len(texts)} текстов")

print(f"\nВсего текстов для обучения: {len(all_texts)}")

# ------------------------------------------------------------
# 2. Предобработка текста (очистка)
# ------------------------------------------------------------
def clean_text(text):
    # Приведение к нижнему регистру
    text = text.lower()
    # Удаление всего, кроме русских букв, пробелов и ё
    text = re.sub(r'[^а-яё\s]', ' ', text)
    # Удаление лишних пробелов
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Применяем очистку ко всем текстам
cleaned_texts = [clean_text(t) for t in all_texts]

# ------------------------------------------------------------
# 3. Разделение на train и test
# ------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    cleaned_texts, all_labels, test_size=0.2, random_state=42, stratify=all_labels
)

print(f"\nОбучающая выборка: {len(X_train)} текстов")
print(f"Тестовая выборка: {len(X_test)} текстов")

# ------------------------------------------------------------
# 4. Векторизация текста (TF-IDF с уни- и биграммами)
# ------------------------------------------------------------
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

print(f"Размер матрицы признаков (TF-IDF): {X_train_tfidf.shape}")

# ------------------------------------------------------------
# 5. Базовый метод: Логистическая регрессия на TF-IDF
# ------------------------------------------------------------
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train_tfidf, y_train)

y_pred_lr = lr_model.predict(X_test_tfidf)
print("\n=== Логистическая регрессия (TF-IDF) ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
print(classification_report(y_test, y_pred_lr))

# ------------------------------------------------------------
# 6. Альтернативный метод: Multinomial Naive Bayes на CountVectorizer
# ------------------------------------------------------------
count_vectorizer = CountVectorizer(max_features=5000, ngram_range=(1,2))
X_train_bow = count_vectorizer.fit_transform(X_train)
X_test_bow = count_vectorizer.transform(X_test)

nb_model = MultinomialNB()
nb_model.fit(X_train_bow, y_train)

y_pred_nb = nb_model.predict(X_test_bow)
print("\n=== Multinomial Naive Bayes (Bag-of-Words) ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_nb):.4f}")
print(classification_report(y_test, y_pred_nb))

# ------------------------------------------------------------
# 7. Загрузка неизвестных текстов (из папки blok_a_a)
# ------------------------------------------------------------
unknown_folder = os.path.join(BASE_DIR, "blok_a_a")
if not os.path.exists(unknown_folder):
    print(f"\nПапка {unknown_folder} не найдена. Проверьте путь.")
else:
    # Загружаем тексты вручную, сохраняя имена файлов
    unknown_texts = []
    unknown_filenames = []
    for filename in sorted(os.listdir(unknown_folder)):
        if filename.endswith('.txt'):
            filepath = os.path.join(unknown_folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='cp1251') as f:
                    text = f.read()
            unknown_texts.append(text)
            unknown_filenames.append(filename)

    if len(unknown_texts) == 0:
        print("Неизвестные тексты не найдены.")
    else:
        print(f"Найдено неизвестных текстов: {len(unknown_texts)}")
        cleaned_unknown = [clean_text(t) for t in unknown_texts]

        # --------------------------------------------------------
        # 8. Предсказание для неизвестных текстов (Логистическая регрессия)
        # --------------------------------------------------------
        X_unknown_tfidf = tfidf_vectorizer.transform(cleaned_unknown)
        proba_lr = lr_model.predict_proba(X_unknown_tfidf)
        pred_lr = lr_model.predict(X_unknown_tfidf)

        df_lr = pd.DataFrame(proba_lr, columns=lr_model.classes_)
        df_lr.insert(0, 'Текст', unknown_filenames)
        df_lr['Предсказанный автор'] = pred_lr

        print("\n=== Вероятности (Логистическая регрессия) ===")
        print(df_lr.round(3).to_string())

        # --------------------------------------------------------
        # 9. Предсказание для неизвестных текстов (Naive Bayes)
        # --------------------------------------------------------
        X_unknown_bow = count_vectorizer.transform(cleaned_unknown)
        proba_nb = nb_model.predict_proba(X_unknown_bow)
        pred_nb = nb_model.predict(X_unknown_bow)

        df_nb = pd.DataFrame(proba_nb, columns=nb_model.classes_)
        df_nb.insert(0, 'Текст', unknown_filenames)
        df_nb['Предсказанный автор'] = pred_nb

        print("\n=== Вероятности (Multinomial Naive Bayes) ===")
        print(df_nb.round(3).to_string())

        # --------------------------------------------------------
        # 10. Сравнение методов
        # --------------------------------------------------------
        print("\n=== Сравнение методов ===")
        print(f"Точность LR на тесте: {accuracy_score(y_test, y_pred_lr):.4f}")
        print(f"Точность NB на тесте: {accuracy_score(y_test, y_pred_nb):.4f}")

print("\nЛабораторная работа №6 завершена.")