# Architecture

Architecture (as deployed for judging): browser -> EC2 full app
http://16.171.250.54:8000 (FastAPI + OpenCV 5.0.0, single-class product
model, conf 0.10, /health, /api/demo, /api/frame, /api/upload,
/api/baseline, dashboard). Secondary link only: public Lambda
Function URL (eu-north-1, demo-only: GET /health and GET /api/demo only,
no OpenCV, no webcam, no /api/frame). App Runner eu-west-2 was not
deployed and is not the judging path. Diagram: docs/architecture.svg
(EC2-first).

Full local pipeline (not on Lambda): browser (getUserMedia webcam,
canvas -> JPEG ~640px, vanilla JS dashboard, NO inference in browser)
  -> HTTPS POST /api/frame (2-4 FPS, JPEG, in-memory only)
  -> FastAPI + Uvicorn (/health, /api/demo, /api/upload, /api/session
     + static dashboard; OpenCV 5 pipeline: imdecode -> letterbox
     resize + copyMakeBorder -> blobFromImage -> readNetFromONNX
     YOLO26n -> forward -> [1,300,6] decode -> clip boxes ->
     IoU/centroid tracker -> rectangle + putText annotation ->
     imencode; snapshot-only GrabCut; session state in-memory only)
  -> Docker logs on the EC2 instance (latency, errors); Lambda demo
     logs are CloudWatch Logs
  -> S3 (demo images, eval outputs, snapshots/history ONLY if in live path;
     NO live webcam frames by default)

Local-only, NOT on AWS: eval photos and training scripts. GitHub source
repo is the judge-accessible code; EC2 runs a Docker build from it
(399 MB, container Up). No App Runner auto-deploy. Devpost submission
links repo + live endpoint + video + report.

Data flow in one sentence: browser captures -> AWS FastAPI receives ->
OpenCV 5 decodes, letterboxes, runs YOLO26n DNN, tracks, annotates ->
browser displays counts; nothing else stores live frames.

One shelf ROI only (default 0.05, 0.10, 0.95, 0.90 of frame). No 8-zone drawing in v1.
