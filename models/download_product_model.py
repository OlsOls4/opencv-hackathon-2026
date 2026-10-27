"""Verify (or reproduce) the single-class 'product' counter model.

The model is a custom fine-tune, so there is NO hosted download URL —
unlike models/download_model.py for the official COCO YOLO26n asset.
This script verifies a local copy, and if it is missing, prints the
exact reproduction steps instead of silently falling back to COCO.
The dashboard (app/main.py) never falls back to COCO: if this model
is missing, counting is disabled and only drift state is shown.

Verified local model (26 Oct 2026, OpenCV 5.0.0):
  models/product_yolo26n.onnx, 9.4 MB, SHA256:
  aa3210f3b0f7dc56f7877e97003c8cde57d43e61dda38864c630436311cfb708
  Single-tile, conf 0.10, counts on 5 held-out real shelf photos:
  bleach 5/24, lemonade 91/88, cookie 19/20, soda 17/27, wooden 14/16
  (hand total 175, predicted 146, MAE 7.0, exact 0/5).
  See results/counting_work/counting_eval.md for the full table.

Reproduction (run in a separate env with torch + ultralytics;
torch 2.8.0 + torchvision 0.23.0 was the combination that worked —
torch 2.14 broke NMS in the original run):
  1. Build the dataset from HoloSelecta (20 vending images, 807 boxes
     converted to ONE class 'product', tiled 2x2) with
     results/counting_work/build_holo_dataset.py. The dataset used
     for the verified model is results/counting_work/dataset/
     (data.yaml, images/, labels/) — its data.yaml currently carries
     an absolute path, so point it at your copy before training.
  2. Train: python results/counting_work/train_product.py
     (YOLO26n base, 20 epochs, imgsz 640, batch 4, CPU, ~17 min
     on a 2-CPU VM; held-out vending val mAP50 0.778).
  3. Export the trained checkpoint to ONNX (imgsz 640, batch 1,
     no NMS in the graph — the app does its own NMS in
     app/product_counter.py) and save it as models/product_yolo26n.onnx.
  4. Verify: re-run this script (SHA256 must match only if you
     reproduce the exact same run; otherwise verify behaviour with
     tests/test_product_counter.py, which pins the 5 held-out counts
     above — if those counts change, counting_eval.md must be updated).

If you only need the dashboard to run, do NOT substitute the COCO
model: the product counter and the COCO model have different ONNX
output shapes ((1, 5, 8400) vs (1, 300, 6)) and different labels.
"""
import hashlib
import os
import sys

OUT = os.path.join(os.path.dirname(__file__), "product_yolo26n.onnx")
EXPECTED = "aa3210f3b0f7dc56f7877e97003c8cde57d43e61dda38864c630436311cfb708"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    if not os.path.exists(OUT):
        print(f"Product model not present: {OUT}")
        print("There is no hosted download for this custom fine-tune.")
        print("Reproduce it with the steps in this file's docstring,")
        print("then verify with tests/test_product_counter.py.")
        print("The dashboard will run drift-only until then — it will")
        print("NOT fall back to COCO labels.")
        sys.exit(2)
    got = sha256(OUT)
    print(f"SHA256: {got}")
    if got != EXPECTED:
        print("WARNING: SHA256 differs from the verified 26 Oct 2026 run.")
        print("This does not necessarily mean the model is wrong — verify")
        print("behaviour with tests/test_product_counter.py (pinned counts:")
        print("bleach 5, lemonade 91, cookie 19, soda 17, wooden 14).")
        sys.exit(1)
    print("Product model verified.")
