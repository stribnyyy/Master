import os
import random
import shutil

# ========== НАСТРОЙКИ ==========
# Путь к вашим исходным данным (где лежат 51 пара изображение + аннотация)
source_images_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5 CLONE/helmet_data/images/train"
source_labels_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5 CLONE/helmet_data/labels/train"

# Куда будем сохранять новый датасет
dest_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5 CLONE/helmet_data_split"

# Количество изображений для валидации (остальное пойдёт в train)
val_count = 6

# Расширения изображений для поиска
image_extensions = ['.png', '.jpg', '.jpeg']

# ========== 1. СОЗДАЁМ СТРУКТУРУ ПАПОК ==========
for split in ['train', 'val']:
    os.makedirs(os.path.join(dest_dir, 'images', split), exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'labels', split), exist_ok=True)

print("📁 Структура папок создана.")

# ========== 2. СОБИРАЕМ СПИСОК ВСЕХ РАЗМЕЧЕННЫХ ФАЙЛОВ ==========
all_txt_files = [f for f in os.listdir(source_labels_dir) if f.endswith('.txt')]
base_names = [os.path.splitext(f)[0] for f in all_txt_files]

print(f"🔍 Найдено {len(base_names)} размеченных изображений.")

# Перемешиваем для случайного разделения
random.seed(42)  # для воспроизводимости (можно убрать или изменить)
random.shuffle(base_names)

# ========== 3. РАЗДЕЛЯЕМ НА TRAIN И VAL ==========
val_names = base_names[:val_count]
train_names = base_names[val_count:]

print(f"📊 Валидация: {len(val_names)} изображений")
print(f"📊 Обучение: {len(train_names)} изображений")

# ========== 4. ФУНКЦИЯ КОПИРОВАНИЯ ==========
def copy_files(name_list, split):
    for name in name_list:
        # Ищем исходное изображение
        src_img = None
        for ext in image_extensions:
            candidate = os.path.join(source_images_dir, name + ext)
            if os.path.exists(candidate):
                src_img = candidate
                break
        if src_img is None:
            print(f"⚠️ Не найдено изображение для {name}")
            continue

        # Исходная аннотация
        src_label = os.path.join(source_labels_dir, name + '.txt')
        if not os.path.exists(src_label):
            print(f"⚠️ Не найдена аннотация для {name}")
            continue

        # Пути назначения
        dst_img = os.path.join(dest_dir, 'images', split, name + os.path.splitext(src_img)[1])
        dst_label = os.path.join(dest_dir, 'labels', split, name + '.txt')

        # Копируем
        shutil.copy2(src_img, dst_img)
        shutil.copy2(src_label, dst_label)

# ========== 5. КОПИРУЕМ ФАЙЛЫ ==========
copy_files(train_names, 'train')
copy_files(val_names, 'val')

print("✅ Копирование завершено.")