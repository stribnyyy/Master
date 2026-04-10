# -*- coding: utf-8 -*-
"""
Лабораторная работа №7
Выбор оптимального метода анализа данных и построение ансамбля моделей
Датасет: Adult Income (Census Income)
"""

import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ------------------------------------------------------------
# 1. Загрузка данных
# ------------------------------------------------------------
DATA_PATH = "adult.csv"  # или "adult.data" — неважно

# Имена столбцов (как в описании датасета)
column_names = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status',
    'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss',
    'hours-per-week', 'native-country', 'income'
]

# Загружаем, пропуская первую строку (она содержит заголовки)
df = pd.read_csv(DATA_PATH, names=column_names, skipinitialspace=True, skiprows=1)

# Удаляем столбец 'fnlwgt'
df = df.drop('fnlwgt', axis=1)

# Заменяем '?' на NaN и удаляем строки с пропусками
df = df.replace('?', np.nan)
df = df.dropna()

print(f"Размер датасета после удаления пропусков: {df.shape}")
print(df.head())
print("\nПроверка на пропуски:")
print(df.isnull().sum())

# ------------------------------------------------------------
# 2. Предобработка данных
# ------------------------------------------------------------
# Преобразуем целевую переменную в бинарный формат: 0 - <=50K, 1 - >50K
df['income'] = df['income'].map({'<=50K': 0, '>50K': 1})

# Разделяем на признаки и целевую переменную
X = df.drop('income', axis=1)
y = df['income']

# Определяем числовые и категориальные признаки
numeric_features = ['age', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
categorical_features = ['workclass', 'education', 'marital-status', 'occupation',
                        'relationship', 'race', 'sex', 'native-country']

# Создаём преобразователи
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Разделяем на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nОбучающая выборка: {X_train.shape[0]} записей")
print(f"Тестовая выборка: {X_test.shape[0]} записей")

# ------------------------------------------------------------
# 3. Обучение и сравнение базовых моделей
# ------------------------------------------------------------
models = {
    "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
    "K-Nearest Neighbors": KNeighborsClassifier(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42, n_estimators=100)
}

results = {}
print("\nОбучение и оценка моделей...")
for name, model in models.items():
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])

    start_time = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - start_time

    y_pred = pipeline.predict(X_test)

    results[name] = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-score": f1_score(y_test, y_pred),
        "Train Time (s)": round(train_time, 2)
    }
    print(f"✓ {name} (точность: {results[name]['Accuracy']:.4f})")

results_df = pd.DataFrame(results).T
print("\nСводная таблица результатов базовых моделей:")
print(results_df.to_string())

# ------------------------------------------------------------
# 4. Выбор трёх лучших моделей (по F1-score или Accuracy)
# ------------------------------------------------------------
top_models = results_df.sort_values('F1-score', ascending=False).head(3).index.tolist()
print(f"\nТри лучшие модели для стекинга: {top_models}")

base_estimators = [
    ('rf', RandomForestClassifier(random_state=42, n_estimators=100)),
    ('gb', GradientBoostingClassifier(random_state=42, n_estimators=100)),
    ('lr', LogisticRegression(random_state=42, max_iter=1000))
]

# ------------------------------------------------------------
# 5. Построение ансамбля (Stacking)
# ------------------------------------------------------------
stacking_model = StackingClassifier(
    estimators=base_estimators,
    final_estimator=LogisticRegression(random_state=42, max_iter=1000),
    cv=5
)

stacking_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('stacking', stacking_model)
])

print("\nОбучение ансамбля (Stacking)...")
start_time = time.time()
stacking_pipeline.fit(X_train, y_train)
stack_train_time = time.time() - start_time

y_pred_stack = stacking_pipeline.predict(X_test)

stacking_results = {
    "Accuracy": accuracy_score(y_test, y_pred_stack),
    "Precision": precision_score(y_test, y_pred_stack),
    "Recall": recall_score(y_test, y_pred_stack),
    "F1-score": f1_score(y_test, y_pred_stack),
    "Train Time (s)": round(stack_train_time, 2)
}

print("\nРезультаты ансамбля (Stacking):")
for metric, value in stacking_results.items():
    print(f"- {metric}: {value}")

# ------------------------------------------------------------
# 6. Сравнение и выводы
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("СРАВНЕНИЕ ЛУЧШИХ ОДИНОЧНЫХ МОДЕЛЕЙ И АНСАМБЛЯ")
print("=" * 50)
comparison_df = results_df.loc[top_models].copy()
comparison_df.loc['Stacking'] = stacking_results
print(comparison_df[['Accuracy', 'Precision', 'Recall', 'F1-score']].to_string())

best_single_f1 = results_df['F1-score'].max()
stacking_f1 = stacking_results['F1-score']
improvement = stacking_f1 - best_single_f1
print(f"\nУлучшение F1-score ансамблем относительно лучшей одиночной модели: {improvement:+.4f}")
if improvement > 0:
    print("Ансамбль показал лучший результат!")
else:
    print("В данном случае ансамбль не дал прироста, что возможно при малом размере данных или схожести моделей.")