"""OpenCV 5 inference for ShelfScan.

Primary signal: baseline / occupancy drift (frame differencing).
Secondary / confirmatory signal: YOLO26n object counting via OpenCV 5 DNN.
This hierarchy is deliberate: generic COCO classes cannot reliably name
packaged shelf goods, so counting alone must not carry a "gap" claim.
"""
import json
import os
import time

import cv2
import numpy as np

COCO_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "coco80.json")
with open(COCO_PATH, encoding="utf-8") as f:
    COCO_CLASSES = json.load(f)

INPUT_SIZE = 640


def opencv_version():
    return cv2.__version__


class Detector:
    def __init__(self, model_path, conf_threshold=0.35):
        if cv2.__version__ != "5.0.0":
            raise RuntimeError(f"OpenCV 5.0.0 required, got {cv2.__version__}")
        self.net = cv2.dnn.readNetFromONNX(model_path)
        # OpenCV 5 engine API differs by build; prefer ENGINE_OPENCV, fall back to ENGINE_NEW.
        try:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        except Exception:
            pass
        self.conf_threshold = conf_threshold
        self._baseline_gray = None
        self._baseline_roi = None

    def letterbox(self, img):
        h, w = img.shape[:2]
        scale = min(INPUT_SIZE / w, INPUT_SIZE / h)
        nw, nh = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (nw, nh))
        pad_x = (INPUT_SIZE - nw) // 2
        pad_y = (INPUT_SIZE - nh) // 2
        padded = cv2.copyMakeBorder(
            resized, pad_y, INPUT_SIZE - nh - pad_y, pad_x, INPUT_SIZE - nw - pad_x,
            cv2.BORDER_CONSTANT, value=114,
        )
        return padded, scale, pad_x, pad_y

    def detect(self, img):
        """Return (detections, annotated_img, latency_ms).
        detections: list of {label, confidence, box:[x1,y1,x2,y2]} in original coords.
        """
        t0 = time.time()
        padded, scale, pad_x, pad_y = self.letterbox(img)
        blob = cv2.dnn.blobFromImage(padded, 1 / 255.0, (INPUT_SIZE, INPUT_SIZE), swapRB=True)
        self.net.setInput(blob)
        out = self.net.forward()
        if out.shape != (1, 300, 6):
            raise RuntimeError(f"Unexpected DNN output shape {out.shape}, expected (1, 300, 6)")
        h, w = img.shape[:2]
        detections = []
        annotated = img.copy()
        for row in out[0]:
            x1, y1, x2, y2, conf, class_id = row
            if conf < self.conf_threshold:
                continue
            # Coordinates are in letterboxed 640 space; map back.
            ox1 = int(max(0, (x1 - pad_x) / scale))
            oy1 = int(max(0, (y1 - pad_y) / scale))
            ox2 = int(min(w, (x2 - pad_x) / scale))
            oy2 = int(min(h, (y2 - pad_y) / scale))
            if ox2 <= ox1 or oy2 <= oy1:
                continue
            label = COCO_CLASSES[int(class_id)] if int(class_id) < len(COCO_CLASSES) else f"class_{int(class_id)}"
            detections.append({"label": label, "confidence": float(conf), "box": [ox1, oy1, ox2, oy2]})
            cv2.rectangle(annotated, (ox1, oy1), (ox2, oy2), (0, 200, 0), 2)
            cv2.putText(annotated, f"{label} {conf:.2f}", (ox1, max(15, oy1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)
        latency_ms = (time.time() - t0) * 1000.0
        return detections, annotated, latency_ms

    def set_baseline(self, img, roi=(0.05, 0.10, 0.95, 0.90)):
        h, w = img.shape[:2]
        x1, y1, x2, y2 = int(w * roi[0]), int(h * roi[1]), int(w * roi[2]), int(h * roi[3])
        crop = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        self._baseline_gray = cv2.GaussianBlur(gray, (21, 21), 0)
        self._baseline_roi = (x1, y1, x2, y2)
        return True

    def occupancy_state(self, img, roi=(0.05, 0.10, 0.95, 0.90)):
        """Primary shelf-state signal. Returns dict with state and changed_ratio.
        States: Full, Low, Gap, Check shelf, No baseline.
        """
        if self._baseline_gray is None:
            return {"state": "No baseline", "changed_ratio": None, "occupancy_note": "Capture a full-shelf baseline first."}
        h, w = img.shape[:2]
        x1, y1, x2, y2 = self._baseline_roi or (int(w * roi[0]), int(h * roi[1]), int(w * roi[2]), int(h * roi[3]))
        crop = img[y1:y2, x1:x2]
        gray = cv2.GaussianBlur(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        # Resize baseline if frame size changed.
        if gray.shape != self._baseline_gray.shape:
            base = cv2.resize(self._baseline_gray, (gray.shape[1], gray.shape[0]))
        else:
            base = self._baseline_gray
        diff = cv2.absdiff(base, gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        changed_ratio = float(np.count_nonzero(thresh) / thresh.size) if thresh.size else 0.0
        # Lighting / camera-move guard: large mean brightness shift -> Check shelf.
        mean_shift = abs(float(np.mean(gray)) - float(np.mean(base)))
        if mean_shift > 60:
            state = "Check shelf"
        elif changed_ratio < 0.10:
            state = "Full"
        elif changed_ratio < 0.30:
            state = "Low"
        else:
            state = "Gap"
        return {"state": state, "changed_ratio": changed_ratio, "mean_brightness_shift": mean_shift}


def decode_image(data: bytes):
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def encode_jpeg(img):
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()
