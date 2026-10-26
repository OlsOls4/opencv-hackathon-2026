"""Evaluate ShelfScan on eval/images/ against eval/ground_truth.csv.
Writes results/eval_results.json and .csv. Never hand-edit outputs.
Ground truth schema: image,class,manual_count — see eval/README.md.
This script was NOT run on real shelf photos in the v1 build (no photos
were supplied); it is provided so Olly's footage can be scored honestly.
"""
import csv
import json
import os
import sys
sys.path.insert(0, ".")
from app.inference import Detector, decode_image


def main():
    det = Detector("models/yolo26n.onnx")
    rows = []
    with open("eval/ground_truth.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = os.path.join("eval", "images", row["image"])
            if not os.path.exists(path):
                continue
            with open(path, "rb") as fh:
                img = decode_image(fh.read())
            detections, _, latency = det.detect(img)
            pred = sum(1 for d in detections if d["label"] == row["class"]) if row.get("class") else len(detections)
            true = int(row["manual_count"])
            rows.append({"image": row["image"], "true_count": true, "predicted_count": pred,
                         "abs_error": abs(pred - true), "latency_ms": round(latency, 1)})
    os.makedirs("results", exist_ok=True)
    with open("results/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    with open("results/eval_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ["image"]); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} evaluated rows (0 means no eval images were present).")


if __name__ == "__main__":
    main()
