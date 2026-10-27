# Model card — live dashboard counter (27 Oct 2026)

## Live counting model: single-class 'product' YOLO26n

- Model: YOLO26n fine-tuned on HoloSelecta (20 vending images, 807 boxes
  converted to ONE class 'product', tiled 2x2, 20 epochs, CPU, ~17 min)
- File: models/product_yolo26n.onnx, 9.4 MB, local only, NOT committed
  (same rule as the COCO ONNX: fetched/trained, never committed)
- SHA256: aa3210f3b0f7dc56f7877e97003c8cde57d43e61dda38864c630436311cfb708
- Runtime: OpenCV 5 DNN only (cv2.dnn.readNetFromONNX), no PyTorch/Ultralytics at runtime
- Input: letterboxed 640x640, blobFromImage 1/255, swapRB=True, single-tile
- Output: [1, 5, 8400] — [cx, cy, w, h, score] for class 0; NMS in app/product_counter.py
- Confidence default: 0.10, dashboard slider 0.05–0.30 (validated setting 0.10;
  0.35 collapses to MAE 21.6 on the held-out photos)
- Classes: 'product' ONLY. No COCO labels appear on the dashboard.
- Validation (5 real shelf photos never trained on, hand total 175,
  predicted 146, MAE 7.0, exact 0/5): cookie 19/20, lemonade 91/88,
  wooden 14/16, soda 17/27, bleach 5/24 (white-on-white, worst case)
- Latency: ~102–176 ms per image, single-tile, OpenCV 5 CPU — inside
  the ~300 ms dashboard rate
- Limits: counting is an estimate, not an exact stock count; no brand
  or SKU; weakest on white-on-white bottles and occluded cans.
  Shelf-state (baseline drift) remains the primary Gap signal.
- Reproduction: models/download_product_model.py (verifies SHA256;
  if missing, prints the retrain steps from
  results/counting_work/train_product.py). There is no hosted download
  for this custom fine-tune, and the dashboard never falls back to COCO.

## Legacy evaluation model: COCO YOLO26n (NOT used by the dashboard)

- Model: YOLO26 Nano, official Ultralytics v8.4.0 release asset yolo26n.onnx
- File: models/yolo26n.onnx, 9.5 MB
- SHA256: 2e947b787d9e787b93a16772a5f55b1d4d8c4d86f53146149c5d6a642442d6f7
- Output: [1, 300, 6] — [x1, y1, x2, y2, confidence, class_id], end-to-end, no NMS
- Classes: COCO 80 (models/coco80.json)
- Use: legacy evaluation only (app/inference.py Detector.detect(),
  tests/test_inference.py, scripts/evaluate*.py) to reproduce the old
  COCO numbers (MAE 18.4 on the same 5 photos, with wrong labels such
  as a whole shelf as 'refrigerator' and cookie tins as 'cell phone').
- Limits: generic COCO classes cannot reliably name packaged shelf goods;
  dense, small, similarly packaged, occluded, or glare-affected items will
  be missed, merged, or mislabelled. This is why it was removed from
  the dashboard.
