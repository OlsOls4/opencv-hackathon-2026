"""Class-agnostic counting experiments (26 Oct 2026) — NOT a production counter.

Measured on the same 5 countable real-shelf photos (hand total 175)
as the COCO baseline, with the same hand counts and no cherry-picking:

- contour (Canny + external contours): MAE 36.4, bias +25.6
- MSER: MAE 29.6, bias +29.6
- SimpleBlob: MAE 138.8, bias +138.8
- vertical edge peaks (whole image): MAE 16.8, bias -6.4, exact 1/5
  — this last number is SPURIOUS: counts are 28, 30, 27, 27, 31
  regardless of hand count (24, 88, 20, 27, 16). It measures image
  width / column structure, not items, and collapses on multi-row
  shelves (lemonade: predicted 30 vs hand 88).
- contour with large morphological closing: MAE 27.4 to 32.4
  (merges whole rows into single blobs).
- autocorrelation pitch: MAE 41.0 whole-image, 132.2 in 3 bands
  (picks label-text pitch, not item pitch).

COCO baseline for comparison (tiled 3x3, conf 0.35): MAE 18.4,
bias -16.4, exact 0/5. COCO at conf 0.25: MAE 16.0, bias -11.6.

Conclusion: no classical class-agnostic method tested here beats
COCO reliably, and none produces boxes round whole items —
visually verified, contour boxes are caps/label fragments and
MSER boxes are text/graphics fragments. Do NOT wire any of these
into Detector as a headline counter. They are kept here only so
the experiment is reproducible and its failure is documented.
The product headline must remain shelf-state (baseline drift),
not counting. See results/detection_improvement_eval.md.
"""
import cv2
import numpy as np


def _nms(boxes, iou=0.35):
    boxes = sorted(boxes, key=lambda b: -b[4])
    kept = []
    for b in boxes:
        ok = True
        for k in kept:
            ix = max(0, min(b[2], k[2]) - max(b[0], k[0]))
            iy = max(0, min(b[3], k[3]) - max(b[1], k[1]))
            inter = ix * iy
            union = (b[2] - b[0]) * (b[3] - b[1]) + (k[2] - k[0]) * (k[3] - k[1]) - inter
            if union > 0 and inter / union > iou:
                ok = False
                break
        if ok:
            kept.append(b)
    return kept


def contour_boxes(img):
    h, w = img.shape[:2]
    area = h * w
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0).apply(gray)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x, y, ww, hh = cv2.boundingRect(c)
        a = ww * hh
        if a < area * 0.0003 or a > area * 0.08 or hh < 20 or ww < 15 or ww / hh > 4:
            continue
        boxes.append([x, y, x + ww, y + hh, 1.0])
    return _nms(boxes)


def mser_boxes(img):
    h, w = img.shape[:2]
    area = h * w
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mser = cv2.MSER_create()
    mser.setMinArea(int(area * 0.0002))
    mser.setMaxArea(int(area * 0.05))
    mser.setMaxVariation(0.25)
    mser.setMinDiversity(0.2)
    regions, _ = mser.detectRegions(gray)
    boxes = []
    for pts in regions:
        x, y, ww, hh = cv2.boundingRect(pts.reshape(-1, 1, 2))
        if ww < 15 or hh < 20 or ww / hh > 4:
            continue
        boxes.append([x, y, x + ww, y + hh, 1.0])
    return _nms(boxes)


def vertical_peak_count(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    h, w = edges.shape
    band = edges[int(h * 0.15):int(h * 0.85), :]
    col = band.sum(axis=0).astype(float)
    col_s = np.convolve(col, np.ones(15) / 15, mode="same")
    thresh = np.median(col_s) + 0.5 * np.std(col_s)
    peaks = []
    last = -999
    for i, v in enumerate(col_s):
        if v > thresh and (i == 0 or v >= col_s[i - 1]) and (i == len(col_s) - 1 or v >= col_s[i + 1]):
            if i - last > 25:
                peaks.append(i)
                last = i
    return len(peaks)


def count_agnostic(img, method):
    if method == "contour":
        return len(contour_boxes(img))
    if method == "mser":
        return len(mser_boxes(img))
    if method == "vertical_peaks":
        return vertical_peak_count(img)
    raise ValueError(f"Unknown agnostic method: {method}")
