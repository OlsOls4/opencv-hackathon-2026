"""UI tests for the preserved full redesign in results/ui_redesign/.

The live app/static/ files are owned by a parallel UI redesign in the
same build tree, so these tests deliberately do NOT assert on them:
overwriting them would destroy that redesign. To deploy this redesign,
copy results/ui_redesign/{index.html,style.css,app.js} over
app/static/ (same filenames, same /static mount) and re-run this suite
against app/static/ instead.
API routes and inference logic are unchanged; these tests only read
static files."""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDESIGN = os.path.join(BASE, "results", "ui_redesign")


def _read(name):
    with open(os.path.join(REDESIGN, name), encoding="utf-8") as f:
        return f.read()


def test_dashboard_has_shopkeeper_actions_and_state_badge():
    html = _read("index.html")
    for needle in ("stateBadge", "baseBtn", "demoBtn", "camBtn",
                   "Restock complete", "Try the demo shelf"):
        assert needle in html, needle


def test_dashboard_shows_no_debug_or_coco_names():
    for name in ("index.html", "app.js"):
        text = _read(name)
        assert "COCO" not in text
        assert "Latency" not in text
        assert "latency_ms" not in text


def test_dashboard_labels_count_as_estimate():
    html = _read("index.html")
    assert "An estimate, not a stock count" in html


def test_css_has_no_external_requests():
    css = _read("style.css")
    assert "http://" not in css and "https://" not in css and "@import" not in css


def test_js_still_calls_the_same_api_routes():
    js = _read("app.js")
    for route in ("/api/demo", "/api/frame", "/api/upload", "/api/baseline",
                  "/api/snapshot", "/api/session/reset", "/api/export.csv",
                  "/api/alerts/dismiss"):
        assert route in js, route
