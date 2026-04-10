from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.train(
    data='data_split.yaml',
    epochs=50,
    imgsz=640,
    batch=8,                    # если памяти мало, уменьшите до 4
    name='helmet_detector',
    device='mps',               # для Mac M1/M2/M3
    workers=0,
    patience=10,
    verbose=True
)