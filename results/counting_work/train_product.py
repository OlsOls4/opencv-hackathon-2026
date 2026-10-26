from ultralytics import YOLO
model = YOLO("yolo26n.pt")
model.train(data="dataset/data.yaml", epochs=20, imgsz=640, batch=4, workers=1, device="cpu", project="runs", name="product_holo", patience=10, save_period=5, verbose=True)
print("TRAIN_DONE")
