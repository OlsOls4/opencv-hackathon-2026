"""In-dashboard alerts: sustained Gap/Low -> recorded; restock /
re-baseline -> cleared. No external delivery is involved anywhere:
AlertManager only records state in memory (see app/alerts.py).
API wiring is tested via the plain app.main functions (no TestClient,
same pattern as tests/test_api.py) so no model or HTTP server is needed.
"""
import sys
sys.path.insert(0, ".")

from app.alerts import AlertManager

N = 5  # default consecutive-frame rule


def _feed(mgr, state, n, t="2026-10-26T21:00:00Z"):
    out = None
    for _ in range(n):
        out = mgr.update(state, total=3, timestamp=t)
    return out


def test_single_gap_frame_does_not_alert():
    mgr = AlertManager()
    assert mgr.update("Gap", total=3) is None
    assert mgr.active is None and mgr.alerts == []


def test_gap_sustained_five_frames_records_alert():
    mgr = AlertManager()
    assert _feed(mgr, "Gap", N - 1) is None
    alert = _feed(mgr, "Gap", 1)
    assert alert is not None and alert["state"] == "Gap"
    assert alert["status"] == "active"
    assert alert["channel"] == "in-dashboard only"
    assert len(mgr.alerts) == 1


def test_low_sustained_also_alerts():
    mgr = AlertManager()
    alert = _feed(mgr, "Low", N)
    assert alert is not None and alert["state"] == "Low"


def test_flicker_resets_streak_so_no_alert():
    mgr = AlertManager()
    _feed(mgr, "Gap", N - 1)
    mgr.update("Full")
    _feed(mgr, "Gap", N - 1)
    assert mgr.active is None


def test_check_shelf_breaks_streak_but_does_not_clear_active_alert():
    mgr = AlertManager()
    _feed(mgr, "Gap", N)
    assert mgr.active is not None
    mgr.update("Check shelf")
    assert mgr.active is not None  # untrusted frame must not cancel it
    assert mgr.streak == 0


def test_restock_full_clears_alert():
    mgr = AlertManager()
    _feed(mgr, "Gap", N)
    assert mgr.active is not None
    assert mgr.update("Full") is None
    assert mgr.active is None
    assert mgr.alerts[0]["status"] == "cleared"
    assert "restocked" in mgr.alerts[0]["cleared_reason"]


def test_rebaseline_clears_alert():
    mgr = AlertManager()
    _feed(mgr, "Gap", N)
    assert mgr.clear_for_rebaseline() is True
    assert mgr.active is None
    assert mgr.alerts[0]["status"] == "cleared"
    assert "re-baseline" in mgr.alerts[0]["cleared_reason"]


def test_dismiss_suppresses_until_full_then_realerts():
    mgr = AlertManager()
    _feed(mgr, "Gap", N)
    assert mgr.dismiss() is True
    assert mgr.active is None
    assert mgr.alerts[0]["status"] == "dismissed"
    # Same Gap run continues: must not instantly reappear.
    _feed(mgr, "Gap", N)
    assert mgr.active is None
    # After a Full, a new Gap run alerts again.
    mgr.update("Full")
    _feed(mgr, "Gap", N)
    assert mgr.active is not None and len(mgr.alerts) == 2


def test_reset_clears_everything():
    mgr = AlertManager()
    _feed(mgr, "Gap", N)
    mgr.reset()
    assert mgr.active is None and mgr.alerts == [] and mgr.streak == 0


def test_session_and_csv_export_include_alerts():
    import app.main as main
    main.alert_manager.reset()
    main.history.clear()
    try:
        _feed(main.alert_manager, "Gap", N, t="2026-10-26T21:00:00Z")
        main.history.append({"time": "2026-10-26T21:00:00Z", "total": 3,
                             "state": "Gap", "counts": {}, "alert": "Gap"})
        session = main.api_session()
        assert session["active_alert"]["state"] == "Gap"
        assert session["alerts"][0]["channel"] == "in-dashboard only"
        assert main.api_alerts()["active_alert"]["state"] == "Gap"
        assert main.api_alert_dismiss()["status"] == "dismissed"
        assert main.api_session()["active_alert"] is None
        body = main.api_export().body.decode()
        lines = body.strip().splitlines()
        assert lines[0] == "time,total,state,counts,alert"
        assert lines[1].endswith(",Gap")
    finally:
        main.alert_manager.reset()
        main.history.clear()
