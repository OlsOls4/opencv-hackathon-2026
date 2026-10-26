"""Download the official YOLO26n ONNX release asset if models/yolo26n.onnx
is missing, and verify its SHA256. Fails loudly on mismatch.
Committed model SHA256 (v8.4.0 asset, verified 2026-10-26 with OpenCV 5):
2e947b787d9e787b93a16772a5f55b1d4d8c4d86f53146149c5d6a642442d6f7
"""
import hashlib
import os
import urllib.request

URL = "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.onnx"
EXPECTED = "2e947b787d9e787b93a16772a5f55b1d4d8c4d86f53146149c5d6a642442d6f7"
OUT = os.path.join(os.path.dirname(__file__), "yolo26n.onnx")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    if not os.path.exists(OUT):
        print(f"Downloading {URL}")
        urllib.request.urlretrieve(URL, OUT)
    got = sha256(OUT)
    print(f"SHA256: {got}")
    if got != EXPECTED:
        raise SystemExit(f"SHA256 mismatch: expected {EXPECTED}, got {got}")
    print("Model verified.")
