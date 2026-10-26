"""ShelfScan Lambda demo — reproduces the live demo-only endpoint, locally.

Live endpoint (demo-only, judged link)::

    https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/

Deploy note (for the live function this file reproduces)::

    Function name:  shelfscan-demo
    Region:         eu-north-1
    Runtime:        Python 3.14
    Handler:        lambda_demo.handler
    Function URL:   auth NONE (public, so judges can open it in a browser)
    Dependencies:   none — standard library only; zip this single file.

What this reproduces — and only this:

* ``GET /health`` — exactly the live shape::

      {"status": "ok", "service": "ShelfScan", "mode": "lambda-demo",
       "model": "yolo26n.onnx", "opencv": "not-loaded-in-lambda-demo"}

* ``GET /api/demo`` — the live staged illustration: a synthetic sparse
  shelf (3 items) against a synthetic full baseline (8 items).
  ``changed_ratio`` is plain arithmetic, ``(8 - 3) / 8 == 0.625``, and
  the state is ``Gap`` because 0.625 >= the 0.30 Gap threshold used by
  ``app/inference.py:occupancy_state``. ``annotated_image_base64`` is
  null because no image is produced. The ``counts`` key uses
  ``synthetic-item`` to make clear no COCO class was detected.

What this does NOT do (and neither does the live Lambda endpoint):

* No OpenCV import, no NumPy, no YOLO/ONNX inference, no webcam,
  no /api/frame, no upload, no baseline capture, no restock action,
  no session history, no tracking, no annotated image.
* It is stateless: every call returns the same fixed values; nothing
  is stored between invocations and there is no shared baseline to
  corrupt.
* It is NOT the full ShelfScan app. The full FastAPI + OpenCV 5 app
  still requires running this repo locally — see README "How to run"
  (``uvicorn app.main:app``). The local ``/api/demo`` differs by
  design: it runs real drift code on synthetic images and returns
  state Low with total 0, while this demo returns the staged Gap/3.

Local check (no AWS, no dependencies)::

    python lambda_demo.py

Root ``GET /`` returns a small index of the two routes. Its exact
shape was not specified for the live endpoint, so it is a local
convenience only and is not claimed to match the live root response.
Any other path returns a 404 JSON body.
"""

import json

# Synthetic staged figures — fixed constants, not measurements.
# Full baseline: 8 synthetic items (mirrors make_demo_image(full=True)
# in app/main.py, which draws 8 boxes). Sparse shelf: 3 synthetic items
# (mirrors make_demo_image(full=False), which draws 3 boxes).
FULL_BASELINE_ITEMS = 8
SPARSE_ITEMS = 3
GAP_THRESHOLD = 0.30  # same threshold as app/inference.py:occupancy_state

MODEL_NAME = "yolo26n.onnx"


def health_response():
    """Exact live /health shape."""
    return {
        "status": "ok",
        "service": "ShelfScan",
        "mode": "lambda-demo",
        "model": MODEL_NAME,
        "opencv": "not-loaded-in-lambda-demo",
    }


def demo_response():
    """Staged /api/demo illustration. No inference runs here.

    changed_ratio is arithmetic on the staged item figures, not a
    measured drift value: (8 - 3) / 8 = 0.625. The state follows the
    same >= 0.30 rule as the real app's occupancy_state, applied to
    that staged ratio. latency_ms / threshold are null because no
    detector ran and no latency was measured; tracks is empty because
    there is no tracker in this demo.
    """
    changed_ratio = (FULL_BASELINE_ITEMS - SPARSE_ITEMS) / FULL_BASELINE_ITEMS
    state = "Gap" if changed_ratio >= GAP_THRESHOLD else "Low"
    return {
        "counts": {"synthetic-item": SPARSE_ITEMS},
        "total": SPARSE_ITEMS,
        "tracks": [],
        "latency_ms": None,
        "model": MODEL_NAME,
        "threshold": None,
        "state": state,
        "changed_ratio": changed_ratio,
        "baseline_items": FULL_BASELINE_ITEMS,
        "annotated_image_base64": None,
        "mode": "lambda-demo",
        "note": ("Staged illustration only: synthetic sparse shelf vs "
                 "synthetic full baseline. No OpenCV inference ran."),
    }


def _route(event):
    """Extract the request path from a Function URL (v2) event.

    Accepts the Function URL payload (requestContext.http.path or
    rawPath), a plain {"path": ...} test event, and a direct call
    with no path (defaults to /health for a smoke check).
    """
    if not isinstance(event, dict):
        return "/health"
    http_ctx = event.get("requestContext") or {}
    http = http_ctx.get("http") or {}
    path = http.get("path") or event.get("rawPath") or event.get("path")
    if not path:
        return "/health"
    # Normalise: strip a trailing slash except for the root itself.
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path


def handler(event, context=None):
    """AWS Lambda handler for the Function URL (payload format 2.0)."""
    path = _route(event)
    if path == "/health":
        status, body = 200, health_response()
    elif path == "/api/demo":
        status, body = 200, demo_response()
    elif path in ("/", ""):
        status, body = 200, {
            "service": "ShelfScan",
            "mode": "lambda-demo",
            "links": {"health": "/health", "demo": "/api/demo"},
            "note": ("Demo-only endpoint: JSON only, no OpenCV, "
                     "no webcam, no /api/frame."),
        }
    else:
        status, body = 404, {"error": "not found",
                             "available": ["/health", "/api/demo"]}
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    # Local smoke check: print both reproduced responses.
    for route in ("/health", "/api/demo"):
        resp = handler({"requestContext": {"http": {"path": route,
                                                    "method": "GET"}}})
        print(route, "->", resp["statusCode"])
        print(resp["body"])
