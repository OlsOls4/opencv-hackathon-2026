# ShelfScan

**One shelf, one camera, one area.** ShelfScan watches a shop shelf with a
webcam and shows Full / Low / Gap / Check shelf states on a dashboard.

**Never miss an empty shelf again — start here, in 30 seconds:**
1. Open the live full app on AWS EC2: http://16.171.250.54:8000
2. Open http://16.171.250.54:8000/health — it returns OpenCV 5.0.0.
3. Open http://16.171.250.54:8000/api/demo — it returns the demo shelf
   state (Low, changed 0.216, re-verified 27 Oct 2026 05:27 GMT).
To use the webcam dashboard, baseline, and restock flow with your own
camera, run the full FastAPI app from this repo locally; see
"How to run" below. Demo video (2:00, counting + shelf state, no
burned-in subtitles, captions via YouTube):
https://www.youtube.com/watch?v=62QhywyJCFQ — Devpost project:
https://devpost.com/software/shelfscan-tm39q7

**Honest scope (v1):** Baseline a full shelf, then live Full / Low / Gap /
Check shelf states, restock confirmation (see below), history + CSV.
Baseline/occupancy drift is the primary signal; counting is a secondary
estimate only, never an exact stock count. No brand/SKU recognition,
no POS, no mobile app, no login, no COOL/Agentic special awards.
What is new here is scope and signal hierarchy, not a new algorithm:
one fixed ROI, drift as primary, counting as a single-class
"product" estimate (MAE 7.0 on 5 held-out real shelf photos, no brand
or SKU — see docs/TECHNICAL_REPORT.md §12). Counting on the live
dashboard is single-class "product" only; no COCO labels are shown
on the dashboard.
A secondary demo-only JSON link is
https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/
— it returns JSON only, runs no OpenCV inference, and has no webcam,
upload, baseline, or restock actions. The demo shelf inside the app is
synthetic and labelled as staged footage; the evaluation photos used
for counting and drift are real shelf photos, as stated in the report.

**Shelf states (from baseline drift, not from the item count):**
Full — changed under 10%, shelf looks like the full baseline, no action.
Low — changed 10–30%, some items missing, check soon.
Gap — changed 30% or more, a clear empty area, restock now.
Check shelf — large brightness/camera shift, do not trust the state;
re-check lighting and camera position, then re-capture the baseline
if the shelf is full. The item count is a secondary estimate only
(single-class "product", no brand or SKU) and must not be used for
stock or ordering.

**Restock flow:** 1) Restock the shelf fully. 2) Click
"✓ Restock complete — capture full shelf", or "Set full shelf from
a photo" (no camera needed). 3) The state should return to Full.
Re-baselining is the restock confirmation, and it also clears any
active in-dashboard alert.

**Alerts (in-dashboard only):** a Gap or Low state sustained for 5
consecutive processed frames records an alert, shown as a banner in
the dashboard (state + time, dismissable) and exported via
`/api/export.csv` (alert column) and `/api/session` (`active_alert` /
`alerts`). A single Gap/Low frame does not alert, and a single
`/api/demo` call (one frame) does not alert on its own. No SMS, email,
push, or sound notification is sent. An alert clears when the state
returns to Full, on re-baseline, on dashboard dismiss (suppressed for
that Gap/Low run), or on session reset.

**Note on /api/demo:** the local app and the Lambda demo return
different demo results by design. Locally, /api/demo shows the synthetic
shelf state from baseline drift (see the smoke test in
docs/TECHNICAL_REPORT.md); the synthetic coloured rectangles give
0 COCO detections, so the state change comes from drift, not counting.
On Lambda, the response is a staged JSON illustration
(synthetic-item: 3, Gap) with no OpenCV inference and no annotated
image. Neither result is a real shelf count.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import cv2; print(cv2.__version__)"   # must print 5.0.0
python models/download_model.py   # only if models/yolo26n.onnx is missing
python models/download_product_model.py  # verifies product model SHA256; prints retrain steps if the local-only ONNX is absent — counting is then disabled, never falls back to COCO
python scripts/smoke_test.py       # with server running, see below
uvicorn app.main:app --host 0.0.0.0 --port 8000
docker build -t shelfscan . && docker run -p 8000:8000 shelfscan
```

Docker from a fresh GitHub clone: the Dockerfile now runs
`python models/download_model.py` (SHA256-verified) during the build,
because the ONNX file is not committed. Docker build PASSED on AWS
EC2 (27 Oct 2026, image shelfscan:latest, 399 MB, container Up,
/health OpenCV 5.0.0, /api/demo Low 0.216). No digest was recorded
for the locally built image; do not claim a registry digest.
Tiled mode is stills-only: high-resolution tiled inference takes
~1.27 s, so it cannot sustain the 2–4 FPS webcam loop.

Endpoints: `GET /health`, `GET /`, `POST /api/frame`, `POST /api/upload`,
`POST /api/baseline`, `POST /api/snapshot`, `GET /api/demo`,
`GET /api/session`, `POST /api/session/reset`, `GET /api/export.csv`,
`GET /api/alerts`, `POST /api/alerts/dismiss`.
`/health` is a liveness check only — it reports the local OpenCV
version and whether a detector has been loaded, it does not prove a
successful inference until /api/demo also succeeds.

## Lambda demo code (reproducibility)

`lambda_demo.py` (repo root, standard library only, handler
`lambda_demo.handler`) reproduces the live demo-only endpoint
(function `shelfscan-demo`, eu-north-1, Python 3.14, public Function
URL, auth NONE — deploy note in the file docstring and in
`docs/LAMBDA_DEMO.md`). It returns the same `/health` and `/api/demo`
shapes, statelessly, with no OpenCV import and no fake inference.
Stated honestly: this reproduces the demo endpoint only, not the
full FastAPI OpenCV 5 app, and the full app still requires running
the repo locally (see "How to run"). Check it with
`python lambda_demo.py` or
`python -m pytest tests/test_lambda_demo.py -q`.

## Architecture

Browser captures (getUserMedia, JPEG ~640px, 2–4 FPS) → HTTPS POST
/api/frame → FastAPI + OpenCV 5 pipeline (imdecode → letterbox →
blobFromImage → YOLO26n ONNX DNN → [1,300,6] decode → IoU/centroid
tracker → annotation) → browser displays counts.
Live webcam frames are processed in memory and NOT stored by default;
only an explicit Save snapshot action stores an image.

**As deployed for judging:** browser → public EC2 endpoint
http://16.171.250.54:8000 (t3.micro, eu-north-1, full FastAPI +
OpenCV 5 app, Docker). A secondary public Lambda Function URL
(eu-north-1, demo-only: GET /health and GET /api/demo only, no
OpenCV, no webcam, no /api/frame) is kept for JSON-only checks.
App Runner eu-west-2 was not deployed and is not the judging path;
`apprunner.yaml` and `docs/DEPLOYMENT.md` are superseded plans,
retained for reference only.
Reproducibility: the Lambda demo is reproduced in this repo by
`lambda_demo.py` (repo root, standard library only — see
`docs/LAMBDA_DEMO.md`). It returns the same `/health` and `/api/demo`
shapes as the live endpoint, statelessly and with no OpenCV import
and no fake inference: `/api/demo` is a staged illustration
(synthetic sparse shelf, total 3, Gap, changed_ratio 0.625 against a
full baseline of 8, annotated image null). This reproduces the demo
endpoint only, not the full FastAPI OpenCV 5 app — the full app still
requires running this repo locally (see "How to run" above). No Lambda
latency, memory, or cost figure is claimed here, because none has been
measured on Lambda; local figures are local only and must not be
presented as Lambda figures. The live function was deployed from code
outside this repo, so `lambda_demo.py` is a reproduction of its
observed responses, not a byte-for-byte copy of the originally
deployed source.

See `docs/architecture.md`, `docs/TECHNICAL_REPORT.md`,
`docs/EVALUATION.md`, `docs/DEPLOYMENT.md`, `docs/VIDEO_SCRIPT.md`.

## Limits, stated plainly

- Generic COCO classes cannot reliably name packaged shelf goods.
  HoloSelecta vending transfer (20 images, local, conf 0.35):
  single-tile MAE 38.05, tiled 3×3 MAE 26.35, pred 310 / GT 807,
  exact 0/20 — counting is reported as a failure, not a feature claim.
- Baseline drift thresholds (Full <0.10, Low <0.30 changed_ratio,
  brightness guard >60, plus phase <0.10 and shift >10 px camera
  guards in `app/inference.py:occupancy_state`) are initial defaults,
  now validated on a real-photo simulated gap and on 24 online
  videos (322 frames, false Gaps 50 → 5 with both guards), but not
  on a real physical removal pair or a shop pilot. Gap is observed
  only for a whole-row removal inside one shelf area (Gap 0.4864);
  small central gaps are missed. Camera movement is guarded, not
  solved; gradual lighting change, occlusion, and restock
  confirmation remain untested. No real-shelf accuracy is claimed.
- Real shelf stills, single-class product counting (see
  docs/TECHNICAL_REPORT.md §12): 5 countable photos never trained
  on, hand total 175, predicted 146, MAE 7.0, bias −5.8, exact 0/5;
  a 6th image was qualitative only (not reliably countable).
  Generic COCO counting on the same 5 photos was MAE 18.4 with
  wrong labels. Counting is an estimate, not an exact stock count;
  drift remains the primary Gap signal. A real physical
  before/after drift pair has still not been tested; only a
  simulated gap on a real photo has.
- Demo images are synthetic; real-shelf drift evaluation still needs
  staged before/after shelf photos with hand counts (see
  `eval/README.md`).
- Single view: hidden/occluded items cannot be detected.
- Alerts, stated plainly: v1 has an in-dashboard alert only (Gap/Low
  sustained for 5 consecutive frames; banner, session history, CSV) —
  no push, email, SMS, or sound notification is sent, so an alert is
  only visible to someone watching the dashboard. No time saved,
  lost-sales avoided, or owner-feedback result is claimed, because
  no shop pilot or real-shelf before/after test has been run yet.
  The benefit to a single owner-manager is a hypothesis to be tested
  in a pilot, not a demonstrated outcome.
- Session state is shared, not per-user: the demo overwrites the
  shared baseline, and two judges/tabs can corrupt each other's
  tracking/history. The local server has no login or rate limiting.
- Privacy and retention: point the camera at the shelf only, not at
  staff, customers, or till areas. Live frames are processed in memory
  and are not stored by default; only an explicit Save snapshot stores
  an image, and session history is held in memory only (last 200
  entries) and cleared on restart/reset — there is no retention period
  beyond the live session, and no facial recognition or audio is used.
  If a person enters the frame, re-aim the camera and delete any
  snapshot containing them. The public demo link has no login; share
  it only with judges.
- No secrets, tokens, AWS keys, or personal photos are in this repo.
