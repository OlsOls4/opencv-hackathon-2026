"""In-dashboard shelf alerts only.

Rule (documented, deliberately simple): a shelf state of Gap or Low must
persist for ALERT_CONSECUTIVE_FRAMES consecutive processed frames
(default 5; at the dashboard webcam rate of ~300 ms/frame that is
~1.5 s) before an alert is recorded. A single Gap/Low frame — e.g. a
brief occlusion or a one-frame drift flicker — does not alert, and a
single /api/demo call (one frame) does not alert on its own.

No SMS, email, push, or sound delivery exists anywhere in this module:
an alert is a record in session history, shown as a banner in the
dashboard, and exported via /api/export.csv and /api/session. Nothing
here claims a pilot, lost sales avoided, or time saved.

Clearing:
- State returns to Full -> active alert cleared (restock confirmed by
  the state itself, not by a claim about sales).
- Re-baseline (the documented restock confirmation) -> active alert
  cleared.
- Dismiss in the dashboard -> active alert marked dismissed and
  suppressed while the same Gap/Low run continues, so it does not
  instantly reappear on the next frame. Suppression lifts when the
  state returns to Full, so a later Gap/Low run alerts again.
- "Check shelf" / "No baseline" break the streak (the state is
  untrusted or unknown) but do NOT clear an existing active alert:
  an unreliable frame must not silently cancel a real gap.
"""

import time

ALERT_STATES = ("Gap", "Low")
DEFAULT_CONSECUTIVE_FRAMES = 5


def _now(timestamp=None):
    return timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class AlertManager:
    def __init__(self, consecutive_frames=DEFAULT_CONSECUTIVE_FRAMES):
        self.consecutive_frames = int(consecutive_frames)
        self.streak = 0
        self.active = None  # dict, also referenced from self.alerts
        self.alerts = []  # history, most recent last; capped at 50
        self._suppressed = False

    def _finish_active(self, status, reason, timestamp):
        if self.active is None:
            return False
        self.active["status"] = status
        self.active["cleared_at"] = _now(timestamp)
        self.active["cleared_reason"] = reason
        self.active = None
        return True

    def update(self, state, total=None, timestamp=None):
        """Feed one processed frame's state. Returns the active alert or None."""
        ts = _now(timestamp)
        if state in ALERT_STATES:
            self.streak += 1
            if self.active is not None:
                # Same sustained run, state moved Gap <-> Low: follow the
                # latest state so the banner never shows a stale one.
                self.active["state"] = state
                self.active["total"] = total
                self.active["updated_at"] = ts
            elif not self._suppressed and self.streak >= self.consecutive_frames:
                self.active = {"state": state, "triggered_at": ts, "total": total,
                               "status": "active",
                               "channel": "in-dashboard only"}
                self.alerts.append(self.active)
                self.alerts[:] = self.alerts[-50:]
            return self.active
        if state == "Full":
            self.streak = 0
            self._suppressed = False
            self._finish_active("cleared", "restocked (state returned to Full)", ts)
            return None
        # "Check shelf", "No baseline", or anything unknown: break the
        # sustained run, but do not clear an existing alert on an
        # untrusted frame.
        self.streak = 0
        return self.active

    def dismiss(self, timestamp=None):
        """Dashboard dismiss: marks the active alert dismissed and
        suppresses re-triggering for the current Gap/Low run."""
        if self.active is None:
            return False
        self._finish_active("dismissed", "dismissed in dashboard", timestamp)
        self.streak = 0
        self._suppressed = True
        return True

    def clear_for_rebaseline(self, timestamp=None):
        """Restock confirmation: re-baselining clears any active alert."""
        self.streak = 0
        self._suppressed = False
        return self._finish_active("cleared", "re-baseline (restock confirmation)", timestamp)

    def reset(self):
        self.streak = 0
        self.active = None
        self.alerts = []
        self._suppressed = False
