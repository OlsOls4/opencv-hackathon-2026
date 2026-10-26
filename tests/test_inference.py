import sys
sys.path.insert(0, ".")
import numpy as np
from app.inference import Detector


def test_opencv_version_and_output_shape():
    import cv2
    assert cv2.__version__ == "5.0.0"
    det = Detector("models/yolo26n.onnx")
    img = np.full((480, 640, 3), 200, dtype=np.uint8)
    detections, annotated, latency = det.detect(img)
    assert annotated.shape == img.shape
    assert latency >= 0


def test_camera_move_guard():
    """Moving-camera / different-scene frame must be Check shelf, not Gap.

    Same-scene controls (identical frame, and a whole-row removal on a
    real shelf photo) must NOT trip the guard. Uses real local files
    when present; skips if the drift-pair fixtures are absent.
    """
    import os
    import cv2
    full_path = "results/real_shelf_images/lemonade_bottles.jpg"
    gap_path = "results/real_drift_pair/lemonade_gap_row.jpg"
    other_path = "results/real_shelf_images/soda_cans.jpg"
    if not (os.path.exists(full_path) and os.path.exists(gap_path) and os.path.exists(other_path)):
        import pytest
        pytest.skip("drift-pair fixtures not present")
    det = Detector("models/yolo26n.onnx")
    full = cv2.imread(full_path)
    # Single-shelf ROI, as in the drift-pair evaluation: whole-image ROI
    # dilutes a row removal to Low, the single-row ROI gives Gap.
    roi = (0.02, 0.36, 0.98, 0.70)
    det.set_baseline(full, roi=roi)
    assert det.occupancy_state(full, roi=roi)["state"] == "Full"
    gap = det.occupancy_state(cv2.imread(gap_path), roi=roi)
    assert gap["state"] == "Gap", gap
    assert gap["phase_correlation_response"] is not None and gap["phase_correlation_response"] >= 0.10
    other = det.occupancy_state(cv2.imread(other_path), roi=roi)
    assert other["state"] == "Check shelf", other
    assert other["phase_correlation_response"] is not None and other["phase_correlation_response"] < 0.10


def test_letterbox_roundtrip():
    det = Detector("models/yolo26n.onnx")
    img = np.zeros((300, 500, 3), dtype=np.uint8)
    padded, scale, px, py = det.letterbox(img)
    assert padded.shape == (640, 640, 3)
