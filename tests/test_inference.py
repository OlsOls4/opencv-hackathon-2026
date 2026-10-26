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


def test_letterbox_roundtrip():
    det = Detector("models/yolo26n.onnx")
    img = np.zeros((300, 500, 3), dtype=np.uint8)
    padded, scale, px, py = det.letterbox(img)
    assert padded.shape == (640, 640, 3)
