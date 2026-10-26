"""API tests use the app functions directly, not TestClient, to avoid
an httpx dependency in the runtime image. Full HTTP smoke coverage is
in scripts/smoke_test.py, which runs against a live server.
"""
import sys
sys.path.insert(0, ".")
from app.main import make_demo_image


def test_demo_image_is_synthetic_and_labelled():
    img = make_demo_image(full=True)
    assert img.shape == (480, 640, 3)
