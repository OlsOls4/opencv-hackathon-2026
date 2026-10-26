"""Simple IoU/centroid tracker. NOT per-object CSRT (too heavy/fragile overnight).

Visible now = active tracks in latest frame (headline).
Unique seen this session = distinct IDs ever created (secondary only).
If an item leaves view for a long time and returns, it may get a new ID.
That is acceptable for a visible-count dashboard, not a warehouse audit.
"""
import math


def _iou(a, b):
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1]); x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1]); area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / max(1, area_a + area_b - inter)


class Tracker:
    def __init__(self, max_missed=5):
        self.max_missed = max_missed
        self.tracks = {}  # id -> {box, label, missed}
        self.next_id = 1
        self.unique_seen = 0

    def update(self, detections):
        # Greedy matching by IoU, centroid distance as tie-breaker.
        used = set()
        new_tracks = {}
        for det in detections:
            box, label = det["box"], det["label"]
            best_id, best_score = None, 0.0
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            for tid, tr in self.tracks.items():
                if tid in used:
                    continue
                score = _iou(box, tr["box"])
                if score > best_score:
                    best_score, best_id = score, tid
            if best_id is not None and best_score > 0.3:
                new_tracks[best_id] = {"box": box, "label": label, "missed": 0}
                used.add(best_id)
            else:
                tid = self.next_id; self.next_id += 1; self.unique_seen += 1
                new_tracks[tid] = {"box": box, "label": label, "missed": 0}
        for tid, tr in self.tracks.items():
            if tid not in used and tr["missed"] + 1 <= self.max_missed:
                new_tracks[tid] = {"box": tr["box"], "label": tr["label"], "missed": tr["missed"] + 1}
        self.tracks = new_tracks
        visible = [t for t in self.tracks.values() if t["missed"] == 0]
        return {"visible": len(visible), "unique_seen": self.unique_seen,
                "tracks": [{"id": tid, "label": t["label"], "box": t["box"]} for tid, t in self.tracks.items() if t["missed"] == 0]}

    def reset(self):
        self.tracks = {}; self.next_id = 1; self.unique_seen = 0
