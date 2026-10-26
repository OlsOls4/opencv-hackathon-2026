# Model card — YOLO26n

- Model: YOLO26 Nano, official Ultralytics v8.4.0 release asset yolo26n.onnx
- File: models/yolo26n.onnx, 9.5 MB
- SHA256: 2e947b787d9e787b93a16772a5f55b1d4d8c4d86f53146149c5d6a642442d6f7
- Runtime: OpenCV 5 DNN only (cv2.dnn.readNetFromONNX), no PyTorch/Ultralytics at runtime
- Input: letterboxed 640x640, blobFromImage 1/255, swapRB=True
- Output: [1, 300, 6] — [x1, y1, x2, y2, confidence, class_id], end-to-end, no NMS
- Confidence default: 0.35, dashboard slider 0.25–0.60
- Classes: COCO 80 (models/coco80.json)
- Limits: generic COCO classes cannot reliably name packaged shelf goods;
  dense, small, similarly packaged, occluded, or glare-affected items will
  be missed, merged, or mislabelled. Counting is secondary to baseline
  occupancy drift in ShelfScan.
- Export recipe (separate export env only): see scripts/export_yolo26.py
  (imgsz=640, batch=1, dynamic=False, half=False, opset=17, end2end=True, nms=False, device=cpu).
  The committed model was downloaded as the v8.4.0 ONNX asset because a
  Torch/Ultralytics install repeatedly failed to download (554 MB wheel
  stalled at ~176 MB); it was verified with OpenCV 5 to produce [1,300,6].
