import sys
sys.path.insert(0, ".")

# Single-class product counter, trained on HoloSelecta (single class),
# evaluated on real shelf photos that were NEVER trained on.
# Counts below are the OpenCV 5 DNN ONNX counts at conf 0.10, single-tile,
# measured 26 Oct 2026. They pin the counter; if they change, the model
# or post-processor changed, and counting_eval.md must be updated too.
EXPECTED = {
    "bleach_bottles.jpg": 5,
    "lemonade_bottles.jpg": 91,
    "cookie_boxes.jpg": 19,
    "soda_cans.jpg": 17,
    "wooden_bottles.jpg": 14,
}
HAND = {
    "bleach_bottles.jpg": 24,
    "lemonade_bottles.jpg": 88,
    "cookie_boxes.jpg": 20,
    "soda_cans.jpg": 27,
    "wooden_bottles.jpg": 16,
}


def test_product_counter_counts():
    import os
    import cv2
    from app.product_counter import ProductCounter
    model = "models/product_yolo26n.onnx"
    if not os.path.exists(model):
        import pytest
        pytest.skip("product model not present (fetch/train per counting_eval.md)")
    counter = ProductCounter(model, conf_threshold=0.10)
    total_err = 0
    for name, expected in EXPECTED.items():
        path = f"results/real_shelf_images/{name}"
        if not os.path.exists(path):
            import pytest
            pytest.skip("real shelf fixture not present")
        dets, annotated, latency = counter.count(cv2.imread(path))
        assert len(dets) == expected, (name, len(dets), expected)
        assert annotated.shape == cv2.imread(path).shape
        assert all(d["label"] == "product" for d in dets)
        total_err += abs(len(dets) - HAND[name])
    assert total_err / len(EXPECTED) == 7.0
