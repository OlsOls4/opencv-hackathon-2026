"""Dashboard QA, 27 Oct 2026: camera bug, slider, baseline, reset.

User-reported bug: clicking Start camera on the live http:// EC2 page
gave 'Camera was not allowed'. Root cause: getUserMedia requires a
secure context (https:// or localhost); on http://, mediaDevices is
undefined, so no permission prompt ever appears. The fix is honest
messaging plus camera-free paths (demo, upload, photo baseline), not
a claim that the camera works on http://.
"""
import os
import sys

sys.path.insert(0, ".")

import cv2

import app.main as main


def _static(name):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "app", "static", name), encoding="utf-8") as f:
        return f.read()


def test_slider_is_validated_product_range():
    html = _static("index.html")
    assert 'min="0.05" max="0.30"' in html
    assert 'value="0.10"' in html
    # Old COCO range must not survive: 0.35 collapses the product
    # counter to MAE 21.6 and the server clamps it anyway.
    assert 'min="0.25" max="0.60"' not in html


def test_camera_error_distinguishes_insecure_context():
    js = _static("app.js")
    assert "isSecureContext" in js
    assert "http://" in js
    # The old misleading message must not be the only camera error.
    assert "not because you denied it" in js
    assert "NotAllowedError" in js


def test_camera_stop_button_label_is_correct():
    js = _static("app.js")
    # Stop branch must restore 'Start camera' (it previously left
    # 'Stop camera' on screen after stopping).
    stop_branch = js.split("if (stream) {")[1].split("camBtn.onclick")[0] \
        if "if (stream) {" in js else ""
    assert "Start camera" in stop_branch


def test_photo_can_set_baseline_without_camera():
    html = _static("index.html")
    js = _static("app.js")
    assert "baselineUpload" in html and "baselineUpload" in js
    assert "/api/baseline" in js


def test_reset_clears_baseline():
    det = main.get_detector()
    det.set_baseline(main.make_demo_image(full=True))
    assert det._baseline_gray is not None
    result = main.api_reset()
    assert result["baseline_cleared"] is True
    assert det._baseline_gray is None
    assert det.occupancy_state(main.make_demo_image(full=True))["state"] == "No baseline"


def test_upload_honours_confidence_slider():
    path = "results/real_shelf_images/cookie_boxes.jpg"
    if not os.path.exists(path) or not os.path.exists("models/product_yolo26n.onnx"):
        import pytest
        pytest.skip("product model or fixture not present")
    main.tracker.reset(); main.history.clear(); main.alert_manager.reset()
    # 0.35 is outside the validated product range and must be clamped
    # to 0.30 server-side, exactly as camera frames are.
    result = main._process(cv2.imread(path), conf=0.35)
    assert result["threshold"] == 0.30
    result = main._process(cv2.imread(path), conf=0.10)
    assert result["threshold"] == 0.10
    assert result["total"] == 19
