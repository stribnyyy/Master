import os
import shutil

# ========== НАСТРОЙКИ (ПРОВЕРЬТЕ ПУТИ!) ==========
# Папка с вашими .txt аннотациями от MakeSense.ai
annotations_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5/annotations_yolo_2025-04-09"

# Папка, где лежат ВСЕ исходные изображения (из датасета Hard Hat Workers)
source_images_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5/hard_hat_dataset/images"

# Папка, куда мы собираем данные для YOLO
dest_dir = "/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5/helmet_data"

# ========== СОЗДАЁМ ПАПКИ (на всякий случай) ==========
os.makedirs(os.path.join(dest_dir, "images", "train"), exist_ok=True)
os.makedirs(os.path.join(dest_dir, "labels", "train"), exist_ok=True)

# ========== КОПИРУЕМ ФАЙЛЫ ==========
copied = 0
for txt_file in sorted(os.listdir(annotations_dir)):
    if not txt_file.endswith('.txt'):
        continue

    name = os.path.splitext(txt_file)[0]  # например, "hard_hat_workers0"

    # Путь к исходной аннотации
    src_label = os.path.join(annotations_dir, txt_file)
    # Путь к исходному изображению (может быть .png или .jpg)
    src_img = None
    for ext in ['.png', '.jpg', '.jpeg']:
        candidate = os.path.join(source_images_dir, name + ext)
        if os.path.exists(candidate):
            src_img = candidate
            break

    if src_img is None:
        print(f"⚠️ Не найдено изображение для {name}, пропускаем")
        continue

    # Пути назначения
    dst_img = os.path.join(dest_dir, "images", "train", name + os.path.splitext(src_img)[1])
    dst_label = os.path.join(dest_dir, "labels", "train", txt_file)

    # Копируем
    shutil.copy2(src_img, dst_img)
    shutil.copy2(src_label, dst_label)
    copied += 1

print(f"✅ Успешно скопировано {copied} пар изображение + аннотация.")