"""Snapshot-only GrabCut. Time-boxed: if it does not prove value in a
30-minute spike, cut it. Label honestly in UI/docs as:
"box-seeded foreground mask (GrabCut), not class-level instance segmentation."
It is NOT per-frame segmentation.
"""
import cv2
import numpy as np


def segment_snapshot(img, box):
    x1, y1, x2, y2 = [int(v) for v in box]
    h, w = img.shape[:2]
    x1, y1 = max(0, x1), max(0, y1); x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid box for GrabCut")
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, (x1, y1, x2 - x1, y2 - y1), bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    out_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    overlay = img.copy()
    overlay[out_mask == 1] = (overlay[out_mask == 1] * 0.6 + np.array([0, 200, 0]) * 0.4).astype(np.uint8)
    return overlay
