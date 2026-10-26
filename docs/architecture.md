# Architecture

Architecture (as deployed for judging): browser -> public Lambda
Function URL (eu-north-1, demo-only: GET /health and GET /api/demo only,
no OpenCV, no webcam, no /api/frame). Full FastAPI + OpenCV 5 app
(letterbox -> blobFromImage -> YOLO26n ONNX DNN -> tracker -> baseline
drift) runs locally from this repo only — see "How to run" in README.
App Runner eu-west-2 was not deployed and is not the judging path;
the diagram below is a plan, not a deployment, and must be updated to
the Lambda demo before it is submitted as the deployed architecture.

Full local pipeline (not on Lambda): browser (getUserMedia webcam,
canvas -> JPEG ~640px, vanilla JS dashboard, NO inference in browser)
  -> HTTPS POST /api/frame (2-4 FPS, JPEG, in-memory only)
  -> FastAPI + Uvicorn (/health, /api/demo, /api/upload, /api/session
     + static dashboard; OpenCV 5 pipeline: imdecode -> letterbox
     resize + copyMakeBorder -> blobFromImage -> readNetFromONNX
     YOLO26n -> forward -> [1,300,6] decode -> clip boxes ->
     IoU/centroid tracker -> rectangle + putText annotation ->
     imencode; snapshot-only GrabCut; session state in-memory only)
  -> CloudWatch Logs (latency, errors) — local plan only, not Lambda
  -> S3 (demo images, eval outputs, snapshots/history ONLY if in live path;
     NO live webcam frames by default)

Local-only, NOT on AWS: Olly's machine cv2.VideoCapture(0) demo script
+ eval photos. GitHub source repo -> App Runner auto-deploy (frozen after
submission). Devpost submission links repo + live endpoint + video + report.

Data flow in one sentence: browser captures -> AWS FastAPI receives ->
OpenCV 5 decodes, letterboxes, runs YOLO26n DNN, tracks, annotates ->
browser displays counts; nothing else stores live frames.

One shelf ROI only (default 0.05, 0.10, 0.95, 0.90 of frame). No 8-zone drawing in v1.
