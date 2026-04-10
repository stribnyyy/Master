from ultralytics import YOLO

# Убедимся, что мы в правильной рабочей директории
import os
os.chdir("/Users/evgenijstribnyj/Master/6СЕМ/МСИИ/Лабораторные/Project/MSAI_5 CLONE")

model = YOLO('yolov8n.pt')

results = model.train(
    data='data_split.yaml',      # новый конфиг
    epochs=50,
    imgsz=640,
    batch=8,
    name='helmet_detector_split',  # новое имя эксперимента
    device='mps',
    workers=0,
    patience=20,
    verbose=True,

    exist_ok=True,
    resume=False,

)