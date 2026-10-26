"""Smoke test: /health, /api/demo (no camera), one upload.
Uses urllib only, so it runs without httpx/TestClient.
Run with the server already running, or set BASE_URL.
Exit non-zero on any failure.
"""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.loads(r.read())


def main():
    h = get("/health")
    assert h["status"] == "ok" and h["opencv"] == "5.0.0", h
    print("health OK:", h)
    d = get("/api/demo")
    assert "counts" in d and "state" in d and d.get("annotated_image_base64"), "demo missing fields"
    print(f"demo OK: state={d['state']} total={d['total']} latency={d['latency_ms']}ms")
    # Upload the demo synthetic image is not available as a file, so upload
    # a generated shelf-like image via the app's own demo generator.
    sys.path.insert(0, ".")
    from app.main import make_demo_image
    from app.inference import encode_jpeg
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(encode_jpeg(make_demo_image(full=True))); tmp_path = tmp.name
    import http.client, mimetypes, uuid
    boundary = uuid.uuid4().hex
    with open(tmp_path, "rb") as fh:
        body = fh.read()
    payload = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"demo.jpg\"\r\n"
               f"Content-Type: image/jpeg\r\n\r\n").encode() + body + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/api/upload", data=payload,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        up = json.loads(r.read())
    assert "counts" in up, up
    print(f"upload OK: state={up['state']} total={up['total']}")
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
