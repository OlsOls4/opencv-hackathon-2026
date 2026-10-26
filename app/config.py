"""ShelfScan configuration. All values are overridable by environment variables."""
import os

MODEL_PATH = os.environ.get("MODEL_PATH", "models/yolo26n.onnx")
CONF_THRESHOLD = float(os.environ.get("CONF_THRESHOLD", "0.35"))
MAX_IMAGE_MB = float(os.environ.get("MAX_IMAGE_MB", "5"))
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")
# One shelf ROI, as fractions of width/height. Full frame by default.
# No 8-zone drawing in v1.
ROI = (0.05, 0.10, 0.95, 0.90)
# In-dashboard alerting only (app/alerts.py): a Gap/Low state sustained
# for this many consecutive processed frames records an alert. No
# external notification (SMS/email/push/sound) is implemented.
ALERT_CONSECUTIVE_FRAMES = int(os.environ.get("ALERT_CONSECUTIVE_FRAMES", "5"))
