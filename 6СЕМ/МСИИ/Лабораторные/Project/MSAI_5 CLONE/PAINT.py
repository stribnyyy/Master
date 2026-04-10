from ultralytics import YOLO
import os

# 1. Укажите путь к вашей обученной модели (best.pt)
model_path = "runs/detect/helmet_detector_split/weights/best.pt"

# 2. Загрузите модель
model = YOLO(model_path)

# 3. Укажите путь к изображению, которое хотите проверить
image_path = "forpaint/hard_hat_workers269.png"

# 4. Запустите предсказание
results = model.predict(
    source=image_path,
    save=True,                # сохранить изображение с нарисованными рамками
    conf=0.02,                 # порог уверенности (показывать объекты с вероятностью > 0.5)
    device='mps',             # или 'cpu' для Intel Mac
    show=False              # если True, откроет окно с результатом (может не работать на Mac)
)

# 5. Узнайте, куда сохранился результат
save_dir = results[0].save_dir
print(f"Результат сохранён в папке: {save_dir}")

for result in results:
    boxes = result.boxes
    if boxes is not None and len(boxes) > 0:
        print(f"Найдено объектов: {len(boxes)}")
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            print(f"  - {model.names[cls_id]}: {conf:.2f}")
    else:
        print("Модель не нашла ни одного объекта на этом изображении.")