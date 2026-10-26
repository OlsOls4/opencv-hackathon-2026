# Video script — ready to record, ≤5 minutes, target 3:30–4:30

> Judge note: no submission video link exists in this repo at the time
> of writing; do not cite one until a video is recorded and uploaded.
> Check the actual local /api/demo state before recording — do not
> assume a Full → Low transition; the Lambda demo returns JSON only
> (Gap, synthetic-item: 3, no annotated image) and is not the dashboard.

Olly must record and upload this; Muse cannot appear on camera or upload
to Olly's YouTube/Vimeo/Devpost. Record in one take if possible, captions on,
no copyrighted music/footage, no faces, home shelf only (do not film in a
shop without staff permission).

## Shot list (record in this order, cut in this order)

0:00–0:25 — Hook, demo-first
- On screen: ShelfScan dashboard, "Try demo shelf" clicked, state changes
  Full → Low. Say: "ShelfScan watches one shelf, one camera, and flags
  gaps before a customer finds them."
- On-screen text: "Staged demo — synthetic shelf, labelled as demo"

0:25–1:15 — Baseline, the primary claim
- Show a real staged home shelf (or the demo shelf if no real shelf is
  ready — label it honestly). Capture a "full" baseline, then remove 2
  items, show dashboard state change and changed_ratio.
- Say once, plainly: "Baseline drift is the primary signal. YOLO counting
  is secondary — generic COCO classes cannot name packaged goods."

1:15–2:15 — Numbers, with denominators (fill these in before recording)
- On screen, one card per number, spoken once:
  - HoloSelecta 20 images: GT 807, single-tile MAE 38.05, exact 0/20,
    within ±1 0/20 — "counting fails on dense vending products, and
    we report that, not hide it"
  - Tiled inference (3×3): MAE 26.35 vs 38.05 baseline, pred 310 / GT 807,
    mean latency ~1.27 s (local, not AWS)
  - Local latency: demo 163.8 ms, bus photo 301 ms (local, not AWS)
- Do NOT quote a metric without its n and condition. Do NOT claim
  labelling accuracy from HoloSelecta (COCO ≠ 109 GTIN products).

2:15–3:00 — Architecture + AWS, 45 seconds
- Show docs/architecture.svg, then the live endpoint if it exists:
  GET /health and GET /api/demo in a browser, no camera needed.
- If no endpoint yet, say on camera: "Local demo only at recording
  time — endpoint to follow" — do not fake a live URL.

3:00–3:45 — One honest failure (15 seconds max, captioned)
- Show a HoloSelecta vending image or a low-light/occluded staged shot
  where counting misses. Caption: "Misses hidden / dense items —
  single-view limit."
- Say: "This is why we do not present YOLO count as the shelf signal."

3:45–4:30 — What it is / is not + links
- On screen, full screen for 10 seconds: repo URL
  https://github.com/OlsOls4/opencv-hackathon-2026 , endpoint URL if live,
  OpenCV 5, YOLO26n ONNX, FastAPI.
- Say: "One shelf, one camera, one ROI. No SKU/barcode, no POS, no
  multi-store — v1 only."

## Recording checklist for Olly
- [ ] Staged home shelf, no faces, no audio of other people
- [ ] Baseline shot, then remove-2 shot, then restock-confirm shot
- [ ] Dashboard visible, state labels readable (zoom in post if needed)
- [ ] Numbers card filled from results/ before recording — do not guess
- [ ] Export ≤5 minutes, upload as public or unlisted, paste link into
      Devpost submission (Devpost step is Olly's, not Muse's)

## Do not do in the video
- Do not show stock/public-dataset footage as if it were live webcam
  without a caption.
- Do not claim "works in any shop / on any product".
- Do not claim AWS endpoint, real-shelf accuracy, or eligibility
  unless each is true at recording time.
