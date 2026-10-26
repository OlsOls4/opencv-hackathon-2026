import sys
sys.path.insert(0, ".")
from app.tracker import Tracker


def test_id_persistence_and_reset():
    t = Tracker()
    r1 = t.update([{"label": "bottle", "box": [10, 10, 50, 50]}])
    r2 = t.update([{"label": "bottle", "box": [12, 12, 52, 52]}])
    assert r1["tracks"][0]["id"] == r2["tracks"][0]["id"]
    assert r2["visible"] == 1
    t.reset()
    assert t.unique_seen == 0
