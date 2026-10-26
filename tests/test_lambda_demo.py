"""Tests for the Lambda demo reproduction. Stdlib only — no cv2 needed,
so these run even where OpenCV is unavailable."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lambda_demo


def _body(resp):
    return json.loads(resp["body"])


def test_health_shape():
    assert _body(lambda_demo.handler(
        {"requestContext": {"http": {"path": "/health"}}})) == {
        "status": "ok", "service": "ShelfScan", "mode": "lambda-demo",
        "model": "yolo26n.onnx", "opencv": "not-loaded-in-lambda-demo"}


def test_demo_shape_is_staged_not_inference():
    body = _body(lambda_demo.handler(
        {"requestContext": {"http": {"path": "/api/demo"}}}))
    assert body["total"] == 3
    assert body["state"] == "Gap"
    assert body["changed_ratio"] == 0.625
    assert body["changed_ratio"] == (8 - 3) / 8
    assert body["baseline_items"] == 8
    assert body["annotated_image_base64"] is None
    assert body["counts"] == {"synthetic-item": 3}
    assert body["latency_ms"] is None  # no inference ran, nothing measured


def test_demo_is_stateless():
    first = lambda_demo.handler({"rawPath": "/api/demo"})
    second = lambda_demo.handler({"rawPath": "/api/demo"})
    assert first["body"] == second["body"]


def test_unknown_path_404():
    resp = lambda_demo.handler({"rawPath": "/api/frame"})
    assert resp["statusCode"] == 404


def test_no_opencv_import():
    with open(lambda_demo.__file__, encoding="utf-8") as f:
        src = f.read()
    assert "import cv2" not in src
    assert "import numpy" not in src
    assert "import onnx" not in src
