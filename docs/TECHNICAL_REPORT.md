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
- GitHub push: DONE 26 Oct 2026 (after the earlier 403 on the bulk
  tree API) via single-file writes, verified back from GitHub: 39/40
  UTF-8 files live at https://github.com/OlsOls4/opencv-hackathon-2026 .
  Missing only .github/workflows/test.yml (CI only) — GitHub blocks
  workflow files via API without a workflows permission, which the
  Meta Muse AI app does not have. ONNX model is NOT committed;
  models/download_model.py fetches it.
- AWS deploy: NOT done. See docs/ZERO_COST_AWS.md for the App Runner
  cost math (~$10–$15 for the 27 Oct–10 Nov judging window, not $0)
  and the Lambda always-free-tier alternative, which needs rework.

## Accuracy improvement — tiled inference (26 Oct 2026, verified)
- Problem found: letterboxing a 3456x4608 vending image to 640x640
  shrinks dense small products below reliable detection size.
- Fix implemented in app/inference.py: adaptive detection. Live webcam
  frames (~640px) stay single-tile for speed; images >1200px use 2x2
  tiles, >2000px use 3x3 tiles (20% overlap, label-agnostic NMS IoU 0.5).
- HoloSelecta first 20, same GT, same conf 0.35, local, OpenCV 5.0.0:
  - Single-tile: MAE 38.05, pred 46 / GT 807, exact 0/20, within ±1 0/20
  - 2x2 tiles: MAE 29.90, pred 213, mean latency 541 ms
  - 3x3 tiles (adaptive, now default for high-res): MAE 26.35,
    pred 310 / GT 807, exact 0/20, within ±1 0/20, bias −24.85,
    mean latency ~1.27 s in the tiled eval file
    (see results/holoselecta_tiled_eval_results.csv)
- Honest limit: tiling improves counting by ~31% (MAE 38.05 → 26.35)
  but does NOT fix it. COCO still cannot name crisps/chocolate/cans,
  and "refrigerator" still fires for the whole machine. Counting is
  therefore NOT presented as the primary shelf signal.

## Baseline/occupancy drift — synthetic test (26 Oct 2026, verified)
- Same image as baseline: state Full, changed_ratio 0.0 — correct.
- Synthetic Gap: same image with a central band painted out:
  state Low, changed_ratio 0.250, mean brightness shift 21.2 — correct
  direction (Low, not Gap, because changed_ratio < 0.30 threshold).
- Brightness +80: state Check shelf, changed_ratio 0.958,
  mean shift 71.3 (>60 guard) — correct guard, not a false Gap.
- Limit: this is a synthetic painted-band test on one vending image,
  NOT a real before/after shelf pair. Real drift still needs Olly's
  staged before/after shelf photos.

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
