# ShelfScan — Technical Report (draft, real before/after drift still pending)

> Status at submission: real-shelf counting on single stills is done
> (see §7 and §11: COCO n=5, MAE 18.4, bias −16.4, exact 0/5;
> superseded for counting by the single-class model in §12:
> n=5, MAE 7.0, predicted 146 / hand 175, exact 0/5); real
> before/after drift pairs and any shop pilot are still untested, so
> shelf-impact claims remain unproven. The ≤5-minute demo video
> (4:22) was recorded after this report's earlier draft and predates
> the real-shelf numbers in §7/§11 — use this report, not the video,
> for the latest real-shelf numbers. The only public endpoint is the
> Lambda demo-only URL above. Judges should verify the full OpenCV
> app from the repo locally (README "How to run").
> What is new here is scope and signal hierarchy, not a new algorithm:
> one fixed ROI, baseline/occupancy drift as primary, generic YOLO
> counting demoted to secondary because COCO cannot name packaged
> goods. The pipeline itself uses standard OpenCV techniques and an
> off-the-shelf COCO model.

## Live AWS demo endpoint — demo-only (26 Oct 2026)
- Live AWS endpoint: https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/ — AWS Lambda function shelfscan-demo in eu-north-1, via a public Function URL. Only /health and /api/demo are exposed on this endpoint.
- Demo-only limitation, stated plainly: OpenCV is NOT loaded in the Lambda demo, there is no live webcam or stateful tracking, and there is no /api/frame on Lambda. The full FastAPI app (OpenCV 5.0.0, YOLO26n, confidence 0.35) runs from the repo locally — see "How to run" in README. Do not present the Lambda endpoint as live OpenCV inference.
- Reproducibility: the Lambda demo is now reproduced in this repo by `lambda_demo.py` (see `docs/LAMBDA_DEMO.md`) — same /health and /api/demo shapes, stateless, no OpenCV. It is a reproduction of the live endpoint's observed responses, not a byte-for-byte copy of the originally deployed source. /health is a liveness check only — it does not prove OpenCV 5 or YOLO26n loaded in Lambda. No Lambda latency, memory, or cost figure is claimed here, because none has been measured on Lambda; local figures (e.g. /api/demo 163.8 ms) are local only and must not be presented as Lambda figures.
- Cost, as of 26 Oct 2026: no Lambda cost, billing-alarm, or free-tier usage figure is claimed for the live endpoint, because none has been recorded from Billing after test calls. Lambda compute is expected to sit inside the free tier only if measured usage stays below the account's monthly request and GB-second allowances, shared across all functions in the account and split across the October/November boundary; CloudWatch Logs, ECR storage, and data transfer out are billed separately and are not covered by that statement. The Function URL is public (auth NONE) so judges can open it in a browser — it is shared only in the submission, not promoted publicly, and will be disabled/deleted after judging. No account-credit balance is claimed here.
- Why eu-north-1: App Runner in eu-west-2 was unavailable (no longer accepting new customers from 30 April 2026) and Lambda eu-west-2 was region-blocked for this new account, hence eu-north-1.

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
- AWS deploy: Lambda demo-only endpoint LIVE (26 Oct 2026):
  https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/
  (function shelfscan-demo, eu-north-1, public Function URL, /health and
  /api/demo only). This is NOT the full app: OpenCV is NOT loaded in
  Lambda, no live webcam/stateful tracking, no /api/frame on Lambda.
  The full FastAPI app runs locally from the repo. App Runner in
  eu-west-2 was unavailable (no longer accepting new customers from
  30 April 2026) and Lambda eu-west-2 was region-blocked for this new
  account, hence eu-north-1. See docs/ZERO_COST_AWS.md for the earlier
  App Runner cost math (~$10–$15 for the 27 Oct–10 Nov judging window,
  not $0).

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

## Baseline/occupancy drift — real-photo SIMULATED gap (26 Oct 2026, verified)
- SIMULATED gap, not a real removal: a real Pexels shelf photo
  (lemonade_bottles.jpg, 88 hand-counted) with a contiguous block
  digitally removed and filled with cloned shelf back-panel
  (see results/real_drift_pair.md). Full method, images local only.
- Default whole-image ROI: central block 0.0385 Full; entire middle
  row removed 0.2021 Low; soda_cans central block 0.1015 Low.
  Controls: same image 0.0 Full; brightness +80 Check shelf
  (0.9554, shift 70.17); brightness +20 Full (0.0, shift 19.87).
- Single-shelf ROI (intended deployment, one shelf one ROI):
  middle-row ROI, entire middle row removed = **Gap, 0.4864,
  mean shift 50.85** (below the 60 guard); central block alone =
  0.0851 Full. Soda front-row ROI central block = 0.1466 Low.
- Honest limit: Gap is observable on a real photo ONLY with a
  single-shelf ROI and only for a whole-row removal; small central
  gaps are missed by drift alone, dark bottles vs dark back-panel
  suppresses diff, and the 50.85 mean shift is close to the Check
  guard. No threshold was changed for this test. A real physical
  removal pair is still untested.

1. Problem and primary user: independent convenience-store owner-manager,
   single shop. Shelf checks are manual and skipped; an empty facing is
   often found by a customer, not staff.
2. Solution: one shelf, one camera, one ROI. Baseline a full shelf, then
   live Full / Low / Gap / Check shelf states, restock confirmation,
   history + CSV, and an in-dashboard alert only (Gap/Low sustained for
   5 consecutive frames; banner + session/CSV, no external
   notification). Demo mode first for judges.
3. Architecture: see docs/architecture.md. Full inference runs locally from
   the repo, not in browser; the AWS Lambda endpoint is demo-only (no
   OpenCV, /health and /api/demo only — see "Live AWS demo endpoint" above).
4. OpenCV 5 implementation: letterbox, blobFromImage, YOLO26n DNN [1,300,6],
   confidence 0.35 default, IoU/centroid tracker (max_missed=5), baseline
   differencing/background modelling as PRIMARY, YOLO count secondary.
   Snapshot-only GrabCut, labelled honestly.
5. AWS deployment: Lambda demo-only endpoint in eu-north-1 (see "Live AWS
   demo endpoint" above): function shelfscan-demo, public Function URL,
   /health and /api/demo only — OpenCV NOT loaded, no live webcam/stateful
   tracking, no /api/frame on Lambda. App Runner eu-west-2 was unavailable
   (no longer accepting new customers from 30 April 2026) and Lambda
   eu-west-2 was region-blocked for this new account, hence eu-north-1.
   The full FastAPI app runs locally from the repo. Docker/CloudWatch/S3
   and billing alarm details: see docs/DEPLOYMENT.md. Freeze after submission.
6. How to run: see README. Judge path <2 minutes via /api/demo, no camera.
7. Evaluation: real-shelf counting on single stills now exists
   (results/real_shelf_eval_results.json, separate team, tiled 3×3,
   conf 0.35): 5 countable images, hand total 175, predicted 93,
   MAE 18.4, bias −16.4, exact 0/5; a 6th image was qualitative only
   (not reliably countable). No precision/recall or labelling accuracy
   is claimed, and no real before/after drift pair exists — drift is
   still synthetic-only. The HoloSelecta numbers below are vending
   transfer only. Do NOT read the HoloSelecta numbers below as shelf results:
   HoloSelecta is vending-domain transfer, not a shelf proxy (see
   docs/EVALUATION.md), and the supermarket empty-shelf evaluation is
   BLOCKED at n = 0 (see results/empty_shelf_BLOCKED.md). See
   docs/EVALUATION.md. Do not write metrics first and fit photos to them.
   Failure cases documented: (1) HoloSelecta counting failure
   (single-tile MAE 38.05, tiled MAE 26.35, exact 0/20, COCO label-space
   limit, whole-machine "refrigerator" merges — see
   results/holoselecta_failures.md); (2) synthetic demo shelf, 0 COCO
   detections by design (baseline drift only); (3) supermarket
   empty-shelf evaluation BLOCKED at n=0 (see
   results/empty_shelf_BLOCKED.md). No real-shelf failure cases yet.
   Scope note: no tiled label breakdown, no precision/recall/F1 at
   IoU≥0.50, no latency p95, and no video count-stability result exists
   yet, although docs/EVALUATION.md lists them. Do not quote a labelling
   accuracy or a tiled failure ranking.
   Verified numbers that may be kept, with their correct scope: HoloSelecta
   first 20, single-tile MAE 38.05, tiled (3x3) MAE 26.35, exact 0/20;
   synthetic drift test — same image Full 0.0, synthetic Gap Low 0.250,
   brightness +80 Check shelf.
8. Limitations: single shelf/camera, staged test only, generic detection
   limits, no SKU recognition, no POS integration, single-view occlusion limit.
   Baseline drift thresholds (Full <0.10, Low <0.30, brightness guard 60)
   are initial, unvalidated defaults from a single synthetic painted-band
   test (n=1, not a real before/after shelf pair). The Gap state
   (changed_ratio ≥ 0.30) has not been observed in any test: the synthetic
   "Gap" case returned Low (changed_ratio 0.250). Camera movement, gradual
   lighting change, occlusion, and restock confirmation are untested.
   v1 has an in-dashboard alert only (Gap/Low sustained for 5
   consecutive frames, shown as a dashboard banner and exported via
   /api/session and /api/export.csv) — no push, email, SMS, or sound
   notification is sent, so an alert is only visible to someone
   watching the dashboard. Session state is shared, not per-user.
   The local server has no login or rate limiting. The Dockerfile has not
   been build-tested and the Lambda demo code is not in this repo.
9. Responsible use and privacy: shelf only, no facial recognition, no audio,
   snapshots limited to shelf view, retention/deletion note for demo.
   Point the camera at the shelf only, not at staff, customers, or till
   areas. Live frames are processed in memory and are not stored by
   default; only an explicit Save snapshot stores an image, and session
   history is held in memory only (last 200 entries) and cleared on
   restart/reset — there is no retention period beyond the live session.
   If a person enters the frame, re-aim the camera and delete any
   snapshot containing them. The public demo link has no login; share
   it only with judges.
10. Future work (separated from v1): multi-shelf, SKU work, POS integration,
    real shop pilot — none claimed as done.

11. Counting threshold tuning (26 Oct 2026, local only): the same 5
    countable real-shelf images and hand counts as section 7 were re-run
    with app/inference.py Detector.detect_tiled 3x3, OpenCV 5.0.0, YOLO26n,
    at conf 0.25, 0.35 and 0.50. The 0.35 re-run reproduced the baseline
    exactly (per-image 0, 61, 4, 7, 21; total 93). Full per-image results:
    results/real_shelf_threshold_tuning.csv and .json.
    Per-image predicted (hand in brackets): bleach_bottles [24]: 2 / 0 / 0;
    lemonade_bottles [88]: 72 / 61 / 52; cookie_boxes [20]: 7 / 4 / 0;
    soda_cans [27]: 9 / 7 / 2; wooden_bottles [16]: 27 / 21 / 11
    (order: conf 0.25 / 0.35 / 0.50).
    Summary (n=5): conf 0.25 — MAE 16.0, bias -11.6, exact 0/5, total 117,
    mean tiled latency 4,348 ms; conf 0.35 — MAE 18.4, bias -16.4,
    exact 0/5, total 93, mean 4,302 ms; conf 0.50 — MAE 22.0, bias -22.0,
    exact 0/5, total 65, mean 3,880 ms. Latencies in this run were higher
    than the baseline run (1,209-1,675 ms) and did not vary systematically
    with threshold, so no latency claim is made for any threshold.
    Decision: default UNCHANGED at 0.35 (app/config.py CONF_THRESHOLD).
    The 0.25 MAE gain (18.4 -> 16.0) is not a clear robust win: it is
    driven almost entirely by one image (lemonade_bottles abs error
    27 -> 16, of a 12-point total abs-error improvement), while
    wooden_bottles worsened (abs error 5 -> 11) and exact stayed 0/5 at
    every threshold, with a still-large negative bias at 0.25. Lowering
    the threshold also added a spurious "person" detection on soda_cans.
    Half_empty_shelves.jpg was again excluded (qualitative only).
    Honest limitation, unchanged by tuning: the COCO label-space still
    limits counting — bleach bottles score 0-2 at every threshold,
    cookie boxes are read as "cell phone", and cans/bottles as
    "refrigerator"/"cup", so no threshold fixes the undercount; counting
    remains a secondary signal behind baseline drift.

12. Single-class product counting (26 Oct 2026, local only, held-out
    real-shelf photos — full report: results/counting_work/counting_eval.md)
    The COCO baseline in §7/§11 (MAE 18.4) is superseded for counting
    by a YOLO26n fine-tuned on HoloSelecta (20 vending images, 807
    boxes converted to ONE class "product", 20 epochs, CPU ~17 min)
    and run single-tile via OpenCV 5.0.0 ONNX (app/product_counter.py,
    conf 0.10, ~102-176 ms/image). The 5 real shelf photos below were
    NEVER trained on, so they are held-out for this model; hand counts
    are visual counts (multipack = 1 unit), NOT dataset ground truth.
    No box carries a product name any more: every box is "product",
    which fixes the COCO "cell phone / refrigerator" label errors,
    but does not fix fragment/duplicate boxes.
    Per-image predicted (hand in brackets): bleach_bottles 5 [24];
    lemonade_bottles 91 [88]; cookie_boxes 19 [20]; soda_cans 17 [27];
    wooden_bottles 14 [16]. Total predicted 146 / hand 175,
    MAE 7.0, bias -5.8, exact 0/5 (about ±7 items per photo).
    Held-out vending validation (last 4 HoloSelecta images held out):
    mAP50 0.778, precision 0.80, recall 0.68. Tiled inference was NOT
    used for this counter: tiled boxes are fragments (tiles cut items)
    and must not be shown in a video. Bleach (5/24, white-on-white)
    remains the worst case and must not be a demo hero.
    Claim allowed, and no more: "Counts products on one shelf
    (single class 'product', no brand or SKU names), about ±7 items
    per photo on 5 held-out shelf photos (hand total 175, predicted
    146, MAE 7.0, exact 0/5), best on clear bottle/box rows, weakest
    on white-on-white bottles and occluded cans." NOT claimed: an
    exact stock count, exact inventory, SKU/brand identification, or
    accuracy on shelves unlike the 5 tested. Shelf-state drift
    (Full/Low/Gap) remains the primary Gap signal; counting estimates
    how much is there. The product ONNX weights are local only, not
    committed, same rule as the COCO ONNX; models/download_model.py
    fetches the COCO model and the training script is in
    results/counting_work/train_product.py. Tests: 23 passed (+1
    product-counter test pinning the 5 counts above).

## Live full OpenCV endpoint on AWS EC2 — verified 26 Oct 2026
- EC2: shelfscan-ec2, i-08fc2ac1d0224790b, t3.micro, eu-north-1, Amazon Linux 2023, running, left running through judging (stop/terminate after 10 Nov 2026).
- Public endpoint: http://16.171.250.54:8000 — /health and /api/demo, no app sign-in.
- Docker build test PASSED on EC2: Dockerfile from repo main, exit 0, image shelfscan:latest 387 MB, container Up.
- Verified from outside AWS (26 Oct 2026, 22:19 GMT): /health 200, OpenCV 5.0.0, model_loaded true; /api/demo 200, Low, changed 0.216, latency 162.1 ms.
- Caveats: security group opens TCP 8000 and 22 to 0.0.0.0/0 for demo only — restrict after judging, especially 22. Free-tier cover through 10 Nov is not confirmed from billing; list price 0.0108 USD/hour, account credits shown $120 at that check, current month $0.00. Muse browser itself refused port 8000 (ERR_CONNECTION_REFUSED) while CloudShell and an outside host returned 200 — cause unproven, judges should try from their own browser.
- This EC2 endpoint, not the Lambda demo, is the full OpenCV app on AWS. Lambda demo-only endpoint remains as a secondary judge link.
