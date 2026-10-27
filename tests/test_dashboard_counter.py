"""Dashboard counting must use the single-class 'product' counter only.

Regression test for the 27 Oct 2026 wiring: app/main.py previously
called Detector.detect(), whose COCO labels ('refrigerator',
'cell phone', ...) appeared on the dashboard and contradicted the
Devpost counting claim. After wiring, every dashboard count is
'label == "product"', the model is product_yolo26n.onnx, and a
missing product model disables counting instead of falling back
to COCO.
"""
import os
import sys

sys.path.insert(0, ".")

import cv2
import pytest

import app.main as main

COCO_LABELS = {"refrigerator", "cell phone", "cup", "bottle", "person",
               "book", "tv", "laptop"}


def _reset_session():
    main.tracker.reset()
    main.history.clear()
    main.alert_manager.reset()


def test_dashboard_count_is_product_only():
    path = "results/real_shelf_images/cookie_boxes.jpg"
    model = "models/product_yolo26n.onnx"
    if not (os.path.exists(path) and os.path.exists(model)):
        pytest.skip("product model or real shelf fixture not present")
    _reset_session()
    result = main._process(cv2.imread(path))
    assert result["model"] == "product_yolo26n.onnx"
    assert result["threshold"] == 0.10
    assert result["total"] == 19
    assert result["counts"] == {"product": 19}
    assert result["counting_model"] == "product"
    assert result["coco_labels_on_dashboard"] is False
    assert not (set(result["counts"]) & COCO_LABELS)
    assert all(t["label"] == "product" for t in result["tracks"])


def test_demo_uses_product_counter_not_coco():
    if not os.path.exists("models/product_yolo26n.onnx"):
        pytest.skip("product model not present")
    _reset_session()
    result = main.api_demo()
    assert result["model"] == "product_yolo26n.onnx"
    assert result["coco_labels_on_dashboard"] is False
    assert set(result["counts"]) <= {"product"}
    assert result["state"] in {"Full", "Low", "Gap", "Check shelf", "No baseline"}


def test_missing_product_model_disables_counting_not_coco():
    _reset_session()
    saved_counter, saved_error = main.counter, main._counter_error
    try:
        main.counter = None
        main._counter_error = "simulated missing model"
        img = main.make_demo_image(full=True)
        result = main._process(img)
        assert result["total"] == 0
        assert result["counts"] == {}
        assert result["counting_model"] == "unavailable"
        assert result["coco_labels_on_dashboard"] is False
        assert not (set(result["counts"]) & COCO_LABELS)
    finally:
        main.counter, main._counter_error = saved_counter, saved_error


def test_health_reports_product_counter():
    main.get_counter()
    health = main.health()
    assert health["model"] == "product_yolo26n.onnx"
    assert health["opencv"] == "5.0.0"
    assert health["coco_labels_on_dashboard"] is False
    if os.path.exists("models/product_yolo26n.onnx"):
        assert health["model_loaded"] is True


def test_main_never_calls_coco_detect():
    import inspect
    src = inspect.getsource(main)
    assert "det.detect(" not in src
    assert "Detector(" in src  # drift only, via get_detector()
