"""Evaluate ShelfScan on a video file, frame by frame, using the shipped pipeline.

Usage:
  .venv/bin/python scripts/evaluate_video.py <video.mp4> <label> [--sample-fps 1] [--baseline-frame 0] [--cross-baseline <image.jpg>]

Baseline is frame 0 of the same video by default (so drift measures
camera/scene change within that video, NOT a stock change on one fixed
shelf). Pass --cross-baseline to use a different image as baseline and
label that run as a cross-source control, never as a same-shelf change.

Output: one JSON row per sampled frame on stdout, plus a summary on stderr.
"""
import argparse
import json
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import CONF_THRESHOLD, ROI
from app.inference import Detector
from app.tracker import Tracker


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("label")
    ap.add_argument("--sample-fps", type=float, default=1.0)
    ap.add_argument("--baseline-frame", type=int, default=0)
    ap.add_argument("--cross-baseline", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    step = max(1, int(round(fps / args.sample_fps)))

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    det = Detector(os.path.join(base, "models", "yolo26n.onnx"),
                   conf_threshold=CONF_THRESHOLD)
    tracker = Tracker(max_missed=5)

    rows = []
    prev_ids = set()
    frame_idx = 0
    sampled = 0
    baseline_set = False
    if args.cross_baseline:
        img = cv2.imread(args.cross_baseline)
        if img is None:
            raise SystemExit(f"Could not read cross-baseline image: {args.cross_baseline}")
        det.set_baseline(img, roi=ROI)
        baseline_set = True

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % step == 0:
            t = frame_idx / fps
            if not baseline_set and frame_idx == args.baseline_frame:
                det.set_baseline(frame, roi=ROI)
                baseline_set = True
            t0 = time.time()
            detections, annotated, latency = det.detect(frame)
            track = tracker.update(detections)
            occ = det.occupancy_state(frame, roi=ROI)
            ids = {tr["id"] for tr in track["tracks"]}
            persisted = len(ids & prev_ids)
            prev_ids = ids
            row = {
                "video": args.label,
                "frame_index": frame_idx,
                "time_s": round(t, 2),
                "width": width,
                "height": height,
                "detections": len(detections),
                "labels": {},
                "visible_tracks": track["visible"],
                "unique_seen": track["unique_seen"],
                "track_ids": sorted(ids),
                "track_ids_persisted_from_prev": persisted,
                "state": occ["state"],
                "changed_ratio": occ.get("changed_ratio"),
                "mean_brightness_shift": occ.get("mean_brightness_shift"),
                "phase_correlation_response": occ.get("phase_correlation_response"),
                "camera_shift_px": occ.get("camera_shift_px"),
                "latency_ms": round(latency, 1),
                "total_ms": round((time.time() - t0) * 1000, 1),
            }
            for d in detections:
                row["labels"][d["label"]] = row["labels"].get(d["label"], 0) + 1
            rows.append(row)
            sampled += 1
            if args.out:
                cv2.imwrite(os.path.join(args.out, f"{args.label}_f{frame_idx}.jpg"), annotated)
        frame_idx += 1
    cap.release()

    summary = {
        "video": args.label,
        "path": args.video,
        "fps": fps,
        "total_frames": total,
        "width": width,
        "height": height,
        "sample_fps": args.sample_fps,
        "sampled_frames": sampled,
        "cross_baseline": args.cross_baseline,
        "states": {},
        "mean_detections": round(sum(r["detections"] for r in rows) / len(rows), 2) if rows else 0,
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / len(rows), 1) if rows else 0,
        "mean_changed_ratio": round(sum(r["changed_ratio"] for r in rows if r["changed_ratio"] is not None) / max(1, sum(1 for r in rows if r["changed_ratio"] is not None)), 4) if rows else None,
        "max_unique_seen": max((r["unique_seen"] for r in rows), default=0),
        "frames_with_persisted_track": sum(1 for r in rows if r["track_ids_persisted_from_prev"] > 0),
    }
    for r in rows:
        summary["states"][r["state"]] = summary["states"].get(r["state"], 0) + 1
    print(json.dumps({"summary": summary, "frames": rows}, indent=2))
    print(f"SUMMARY {args.label}: sampled={sampled} states={summary['states']} "
          f"mean_det={summary['mean_detections']} mean_lat={summary['mean_latency_ms']}ms "
          f"unique_seen={summary['max_unique_seen']}", file=sys.stderr)


if __name__ == "__main__":
    main()
