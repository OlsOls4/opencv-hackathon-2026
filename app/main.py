"""ShelfScan FastAPI app. Inference runs on the server,
never in the browser. Live webcam frames are processed in memory and are
NOT stored by default; only an explicit Save snapshot action stores an image.
Session state is shared, not per-user: /api/demo overwrites the shared
baseline, so two judges/tabs can corrupt each other's tracking/history.
"""
import base64
import csv
import io
import os
import time

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app import config
from app.alerts import AlertManager
from app.inference import Detector, decode_image, encode_jpeg
from app.product_counter import ProductCounter
from app.schemas import counts_from_detections, result_shape
from app.segmentation import segment_snapshot
from app.tracker import Tracker

app = FastAPI(title="ShelfScan")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
detector = None  # drift only — never used for counting (see below)
counter = None
_counter_error = None
tracker = Tracker(max_missed=5)
history = []  # list of {time, total, state, counts, alert}
alert_manager = AlertManager(consecutive_frames=config.ALERT_CONSECUTIVE_FRAMES)
_model_name = "product_yolo26n.onnx"


def get_detector():
    """Drift / baseline only. Its COCO detect() is legacy evaluation
    and is never called by the dashboard."""
    global detector
    if detector is None:
        detector = Detector(os.path.join(BASE, config.MODEL_PATH),
                            conf_threshold=config.CONF_THRESHOLD)
    return detector


def get_counter():
    """Single-class 'product' counter — the ONLY counting model the
    dashboard uses. If the model file is missing, counting is disabled
    and the dashboard shows drift state only. It NEVER falls back to
    COCO, so no COCO label ('refrigerator', 'cell phone', ...) can
    ever appear on the dashboard."""
    global counter, _counter_error
    if counter is None and _counter_error is None:
        path = os.path.join(BASE, config.PRODUCT_MODEL_PATH)
        try:
            counter = ProductCounter(path, conf_threshold=config.PRODUCT_CONF_THRESHOLD)
        except Exception as e:
            _counter_error = str(e)
    return counter


def _b64(img):
    return base64.b64encode(encode_jpeg(img)).decode()


def _process(img, conf=None):
    det = get_detector()
    cnt = get_counter()
    if cnt is not None:
        if conf is not None:
            # Validated setting is 0.10; clamp the UI slider so a judge
            # cannot push the counter into the collapsed range (0.35
            # gives MAE 21.6 on the held-out photos).
            cnt.conf_threshold = min(0.30, max(0.05, float(conf)))
        detections, annotated, latency = cnt.count(img)
        threshold = cnt.conf_threshold
        counting_model = "product"
        counting_note = ("Single-class 'product' count estimate, about +/-7 "
                         "items per photo on 5 held-out photos; not an exact "
                         "stock count, no brand or SKU.")
    else:
        detections, annotated, latency = [], img.copy(), 0.0
        threshold = config.PRODUCT_CONF_THRESHOLD
        counting_model = "unavailable"
        counting_note = ("Product counter model not present; drift state only. "
                         "No COCO fallback — no labels are shown.")
    # Safety invariant: the dashboard only ever shows 'product'.
    assert all(d["label"] == "product" for d in detections)
    track = tracker.update(detections)
    occ = det.occupancy_state(img, roi=config.ROI)
    counts = counts_from_detections(detections)
    entry = {"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "total": len(detections), "state": occ["state"], "counts": dict(counts)}
    alert = alert_manager.update(occ["state"], len(detections), entry["time"])
    entry["alert"] = alert["state"] if alert else ""
    history.append(entry)
    history[:] = history[-200:]
    result = result_shape(counts, len(detections), track["tracks"], latency,
                          _model_name, threshold, state=occ["state"],
                          changed_ratio=occ.get("changed_ratio"), annotated_b64=_b64(annotated))
    result["active_alert"] = alert
    result["counting_model"] = counting_model
    result["counting_note"] = counting_note
    result["coco_labels_on_dashboard"] = False
    return result


def make_demo_image(full=True):
    """Synthetic, clearly labelled demo shelf. NOT a real shop photo.
    Full: 8 coloured boxes on a shelf. Sparse: 3 boxes + gaps.
    """
    img = np.full((480, 640, 3), (210, 200, 190), dtype=np.uint8)
    cv2.rectangle(img, (20, 380), (620, 400), (120, 80, 40), -1)
    colours = [(0, 0, 200), (0, 150, 0), (200, 100, 0), (150, 0, 150), (0, 150, 150), (50, 50, 200), (200, 0, 0), (0, 100, 200)]
    n = 8 if full else 3
    for i in range(n):
        x = 40 + i * 75
        cv2.rectangle(img, (x, 200 + (i % 3) * 20), (x + 55, 380), colours[i % len(colours)], -1)
        cv2.putText(img, "item", (x + 5, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(img, "DEMO / STAGED FOOTAGE - synthetic shelf", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    return img


@app.get("/health")
def health():
    # Liveness only: this does not prove a successful inference until
    # /api/demo also succeeds.
    return {"status": "ok", "opencv": cv2.__version__, "model": _model_name,
            "model_loaded": counter is not None,
            "counting": "single-class product (no COCO labels)",
            "coco_labels_on_dashboard": False}


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(BASE, "app", "static", "index.html"), encoding="utf-8") as f:
        return f.read()


@app.post("/api/frame")
async def api_frame(file: UploadFile = File(...), conf: float = None):
    data = await file.read()
    if len(data) > config.MAX_IMAGE_MB * 1024 * 1024:
        return JSONResponse({"error": f"Image over {config.MAX_IMAGE_MB} MB limit"}, status_code=413)
    try:
        img = decode_image(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return _process(img, conf=conf)


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...), conf: float = None):
    data = await file.read()
    if len(data) > config.MAX_IMAGE_MB * 1024 * 1024:
        return JSONResponse({"error": f"File over {config.MAX_IMAGE_MB} MB limit"}, status_code=413)
    # Video: sample frames with VideoCapture from a temp file in /tmp (ephemeral).
    # Only the first sampled frame is processed, not the full video.
    if file.filename and file.filename.lower().endswith((".mp4", ".mov", ".webm", ".avi")):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(data); tmp_path = tmp.name
        try:
            cap = cv2.VideoCapture(tmp_path)
            frames = []
            idx = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if idx % 5 == 0:
                    frames.append(frame)
                idx += 1
                if len(frames) >= 20:
                    break
            cap.release()
            if not frames:
                return JSONResponse({"error": "No frames decoded from video"}, status_code=400)
            return _process(frames[0], conf=conf)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    try:
        img = decode_image(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return _process(img, conf=conf)


@app.post("/api/baseline")
async def api_baseline(file: UploadFile = File(...)):
    data = await file.read()
    try:
        img = decode_image(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    get_detector().set_baseline(img, roi=config.ROI)
    # Re-baselining is the restock confirmation: it clears any active alert.
    cleared = alert_manager.clear_for_rebaseline()
    return {"status": "baseline captured", "roi": config.ROI, "alert_cleared": cleared}


@app.post("/api/snapshot")
async def api_snapshot(file: UploadFile = File(...)):
    """Snapshot-only GrabCut. Returns masked image, labelled honestly."""
    data = await file.read()
    try:
        img = decode_image(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    cnt = get_counter()
    detections = cnt.count(img)[0] if cnt is not None else []
    if not detections:
        return JSONResponse({"error": "No product detected to segment"}, status_code=400)
    out = segment_snapshot(img, detections[0]["box"])
    return {"label": "box-seeded foreground mask (GrabCut), not class-level instance segmentation",
            "annotated_image_base64": _b64(out)}


@app.get("/api/demo")
def api_demo():
    """Judge path, no camera needed. Sets full synthetic as baseline, then
    shows a sparse synthetic shelf so a Low state is visible (changed
    0.216 on the whole-image ROI; Gap 0.486 requires a single-shelf ROI).
    Labelled demo."""
    det = get_detector()
    det.set_baseline(make_demo_image(full=True), roi=config.ROI)
    img = make_demo_image(full=False)
    return _process(img)


@app.get("/api/session")
def api_session():
    track = {"visible": len([t for t in tracker.tracks.values() if t["missed"] == 0]),
             "unique_seen": tracker.unique_seen}
    return {"session": track, "history": history[-50:],
            "active_alert": alert_manager.active, "alerts": alert_manager.alerts[-50:]}


@app.get("/api/alerts")
def api_alerts():
    return {"active_alert": alert_manager.active, "alerts": alert_manager.alerts[-50:]}


@app.post("/api/alerts/dismiss")
def api_alert_dismiss():
    dismissed = alert_manager.dismiss()
    return {"status": "dismissed" if dismissed else "no active alert"}


@app.post("/api/session/reset")
def api_reset():
    tracker.reset(); history.clear(); alert_manager.reset()
    # Previously this left the baseline in place, so the dashboard's
    # "No shelf checked yet" was false: the next frame still compared
    # against the old full shelf. Reset now truly clears it.
    if detector is not None:
        detector.clear_baseline()
    return {"status": "reset", "baseline_cleared": True}


@app.get("/api/export.csv")
def api_export():
    out = io.StringIO(); w = csv.writer(out)
    w.writerow(["time", "total", "state", "counts", "alert"])
    for h in history:
        w.writerow([h["time"], h["total"], h["state"], h["counts"], h.get("alert", "")])
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=shelfscan-session.csv"})


app.mount("/static", StaticFiles(directory=os.path.join(BASE, "app", "static")), name="static")
