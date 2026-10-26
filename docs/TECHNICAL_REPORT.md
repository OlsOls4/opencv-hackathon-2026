# ShelfScan — Technical Report (draft, real shelf evaluation still pending)

## Verified build numbers (local, 26 Oct 2026 — not AWS, not shelf data)
- OpenCV: cv2.__version__ == 5.0.0, verified in the venv, no OpenCV 4 fallback
- Model: YOLO26n ONNX, 9.5 MB, SHA256
  2e947b787d9e787b93a16772a5f55b1d4d8c4d86f53146149c5d6a642442d6f7,
  DNN output verified as [1, 300, 6]
- Smoke test passed: /health returned
  {"status":"ok","opencv":"5.0.0","model":"yolo26n.onnx"};
  /api/demo returned state Low, total 0, latency 163.8 ms;
  upload returned state Full, total 0; /api/session and /api/export.csv worked
- Unit tests: 4 passed (inference version/shape, letterbox, tracker ID
  persistence/reset, demo image)
- Real-object sanity check (NOT a shelf photo): a public bus photo gave
  5 detections in 301 ms — bus 0.92, persons 0.91 / 0.90 / 0.86 / 0.57.
  This proves the DNN path works on real objects; it is NOT shelf
  counting accuracy.
- Honest limitation found in testing: the synthetic demo shelf (coloured
  rectangles) gives 0 COCO detections, as expected — it proves the
  baseline-drift state change (Full to Low), not counting. Real counting
  still needs real shelf photos.
- Dockerfile written but NOT build-tested here: Docker is not available
  in this VM. It needs a Docker test on the deploy machine.
- GitHub push: NOT done at last update — push to
  OlsOls4/opencv-hackathon-2026 returned 403 Resource not accessible by
  integration (read access verified, write access missing). Repo was
  confirmed empty at that check.
- AWS deploy: NOT done. See docs/ZERO_COST_AWS.md for the App Runner
  cost math (~$10–$15 for the 27 Oct–10 Nov judging window, not $0)
  and the Lambda always-free-tier alternative, which needs rework.

1. Problem and primary user: independent convenience-store owner-manager,
   single shop. Shelf checks are manual and skipped; an empty facing is
   often found by a customer, not staff.
2. Solution: one shelf, one camera, one ROI. Baseline a full shelf, then
   live Full / Low / Gap / Check shelf states, restock confirmation,
   history + CSV. Demo mode first for judges.
3. Architecture: see docs/architecture.md. Inference runs on AWS, not in browser.
4. OpenCV 5 implementation: letterbox, blobFromImage, YOLO26n DNN [1,300,6],
   confidence 0.35 default, IoU/centroid tracker (max_missed=5), baseline
   differencing/background modelling as PRIMARY, YOLO count secondary.
   Snapshot-only GrabCut, labelled honestly.
5. AWS deployment: App Runner eu-west-2, Docker, CloudWatch, S3 only if in
   live path, billing alarm, freeze after submission. See docs/DEPLOYMENT.md.
6. How to run: see README. Judge path <2 minutes via /api/demo, no camera.
7. Evaluation: PENDING — no real shelf photos have been supplied yet,
   so no counting MAE/MAPE, precision/recall, or labelling accuracy is
   claimed here. See docs/EVALUATION.md. Do not write metrics first and
   fit photos to them. Include failure cases. The only failure case
   documented so far is the synthetic demo shelf (0 COCO detections,
   expected — baseline drift only).
8. Limitations: single shelf/camera, staged test only, generic detection
   limits, no SKU recognition, no POS integration, single-view occlusion limit.
9. Responsible use and privacy: shelf only, no facial recognition, no audio,
   snapshots limited to shelf view, retention/deletion note for demo.
10. Future work (separated from v1): multi-shelf, SKU work, POS integration,
    real shop pilot — none claimed as done.
