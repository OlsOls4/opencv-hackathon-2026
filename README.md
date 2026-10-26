# ShelfScan

**One shelf, one camera, one area.** ShelfScan watches a shop shelf with a
webcam and flags gaps and low stock before customers notice.

**Honest scope (v1):** Baseline a full shelf, then live Full / Low / Gap /
Check shelf states, restock confirmation, history + CSV. Baseline/occupancy
drift is the primary signal; YOLO counting is secondary/confirmatory.
No 8-zone drawing, no brand/SKU recognition, no POS, no mobile app, no
login, no COOL/Agentic special awards.

**Live demo for judges (no camera needed):** open the endpoint, click
“Try demo shelf”. Demo images are synthetic and labelled as staged footage.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import cv2; print(cv2.__version__)"   # must print 5.0.0
python models/download_model.py   # only if models/yolo26n.onnx is missing
python scripts/smoke_test.py       # with server running, see below
uvicorn app.main:app --host 0.0.0.0 --port 8000
docker build -t shelfscan . && docker run -p 8000:8000 shelfscan
```

Endpoints: `GET /health`, `GET /`, `POST /api/frame`, `POST /api/upload`,
`POST /api/baseline`, `POST /api/snapshot`, `GET /api/demo`,
`GET /api/session`, `POST /api/session/reset`, `GET /api/export.csv`.

## Architecture

Browser captures (getUserMedia, JPEG ~640px, 2–4 FPS) → HTTPS POST
/api/frame → AWS App Runner (FastAPI) → OpenCV 5 pipeline
(imdecode → letterbox → blobFromImage → YOLO26n ONNX DNN → [1,300,6]
decode → IoU/centroid tracker → annotation) → browser displays counts.
Live webcam frames are processed in memory and NOT stored by default;
only an explicit Save snapshot action stores an image.

See `docs/architecture.md`, `docs/TECHNICAL_REPORT.md`,
`docs/EVALUATION.md`, `docs/DEPLOYMENT.md`, `docs/VIDEO_SCRIPT.md`.

## Limits, stated plainly

- Generic COCO classes cannot reliably name packaged shelf goods.
- Single view: hidden/occluded items cannot be detected.
- Demo images are synthetic; real-shelf evaluation requires Olly's staged
  shelf photos with hand-counted ground truth (see `eval/README.md`).
- No secrets, tokens, AWS keys, or personal photos are in this repo.
