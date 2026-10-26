import sys
sys.path.insert(0, ".")
import cv2
from app.agnostic_counting import count_agnostic


def test_agnostic_methods_run_and_do_not_beat_coco_reliably():
    # Same 5 countable real-shelf photos as the COCO baseline.
    # COCO tiled 3x3 conf 0.35: MAE 18.4. These methods must run and
    # must NOT be claimed as a counting improvement: contour and MSER
    # are far worse, and vertical_peaks is a width proxy (see module
    # docstring), so this test pins the measured counts, not a win.
    hand = {"bleach_bottles.jpg": 24, "lemonade_bottles.jpg": 88,
            "cookie_boxes.jpg": 20, "soda_cans.jpg": 27, "wooden_bottles.jpg": 16}
    expected = {
        "contour": {"bleach_bottles.jpg": 60, "lemonade_bottles.jpg": 66,
                    "cookie_boxes.jpg": 90, "soda_cans.jpg": 22, "wooden_bottles.jpg": 65},
        "mser": {"bleach_bottles.jpg": 56, "lemonade_bottles.jpg": 133,
                 "cookie_boxes.jpg": 40, "soda_cans.jpg": 72, "wooden_bottles.jpg": 22},
        "vertical_peaks": {"bleach_bottles.jpg": 28, "lemonade_bottles.jpg": 30,
                           "cookie_boxes.jpg": 27, "soda_cans.jpg": 27, "wooden_bottles.jpg": 31},
    }
    for method, exp in expected.items():
        for fname, want in exp.items():
            img = cv2.imread(f"results/real_shelf_images/{fname}")
            assert img is not None, fname
            got = count_agnostic(img, method)
            assert got == want, (method, fname, got, want)
