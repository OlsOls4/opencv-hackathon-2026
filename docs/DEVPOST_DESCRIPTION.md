# ShelfScan — improved Devpost description (ready to paste)

> PARENT ONLY — DO NOT PASTE THIS NOTE INTO DEVPOST.
> Current live link is v4: https://www.youtube.com/watch?v=62QhywyJCFQ
> Also check before pasting: thumbnail (3:2, JPG/PNG/GIF, max 5 MB),
> image gallery (dashboard screenshot, drift before/after, architecture
> diagram), Built With tags, and Try It Out links — none of these can
> be set from this text file alone.
> No number or link in the text below is invented. Every figure is
> copied from results/ or docs/TECHNICAL_REPORT.md.

---

## ShelfScan — never miss an empty shelf again

**One shop, one shelf, one camera.** ShelfScan watches a single shop
shelf and tells the shopkeeper, in plain words, whether that shelf is
Full, Low, has a Gap, or needs a Check — so an empty facing is found
by staff, not by a customer.

The inversion: most shelf tools lead with counting. ShelfScan leads
with change — how much this shelf differs from its own full baseline
— and treats counting as a rough second signal. That is the whole
design bet.

## Try it in 30 seconds (JSON check, no camera needed)

A. Open the live full app on AWS EC2: http://16.171.250.54:8000
B. Open http://16.171.250.54:8000/health — it returns OpenCV 5.0.0.
C. Open http://16.171.250.54:8000/api/demo — it returns the demo
   shelf state (Low, changed 0.216, re-verified 27 Oct 2026 05:27 GMT).

## Try the full flow (no camera needed)

Try the full flow on EC2, no camera needed: "Try the demo shelf",
or "Set full shelf from a photo", then upload a later photo to see
Full / Low / Gap / Check and the 5-frame alert. Live camera needs
HTTPS or localhost — this EC2 page is HTTP, so the dashboard
explains that and offers the photo path instead. Repo run is only
needed for a live webcam.

## Evidence at a glance — and what to trust it for

- Drift Gap 0.4864 on a whole-row removal only, single-shelf ROI
  (whole-image ROI on the same removal is only Low 0.2021).
- Counting MAE 7.0, n=5, exact 0/5, bleach 5/24, predicted 146
  vs hand 175. The same 5 photos were also used to select
  conf 0.10 among 8 configs; an independent held-out shelf test
  is still pending. Hand-count uncertainty is about ±5 on
  lemonade, ±4 on soda, ±3 on bleach.
- False Gaps 50 → 5 on 24 videos / 322 frames, with phase +
  shift guards. No shop pilot. Impact claims in this submission
  describe intended use, not measured shop results.
- **Trust it only to flag a whole-row gap on one fixed-camera
  shelf. Do NOT use its count for stock or ordering.**

Secondary demo-only link (JSON only, no OpenCV, no webcam):
https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/

## The problem

In a small independent shop, shelf checks are manual and get skipped.
An empty facing is often discovered by a customer, not by staff.
ShelfScan is built for one owner-manager, one shop, one shelf, and
one fixed camera — not for a chain, not for many cameras, and not
for brand or barcode recognition.

## How it works — one journey, start to finish

1. Point a fixed camera at one shelf and capture a "full" baseline
   — or, on this HTTP demo page, use "Set full shelf from a photo"
   (see "Try the full flow" above).
2. ShelfScan compares each new frame with that baseline and shows
   one of four states:
   - **Full** — the shelf looks like the full baseline, no action.
   - **Low** — some items are missing, check soon.
   - **Gap** — a clear empty area, restock now.
   - **Check shelf** — lighting or camera moved, do not trust the
     state; fix the camera or lighting, then re-capture the baseline.
3. A Gap or Low state held for 5 consecutive frames raises an
   in-dashboard alert (banner, session history, CSV export). There
   is no SMS, email, push, or sound alert in v1.
4. Restock the shelf fully, capture a new baseline, and the state
   returns to Full. That re-baseline is the restock confirmation.

What changes for the shopkeeper: morning, capture the full shelf
once. During the day, glance at one word — Full, Low, Gap, Check —
instead of walking the aisle to look. Only a Gap or Low held for 5
frames raises an alert. Restock, re-capture the baseline, done.

## What is new here

The innovation is the inversion, not a new model. Most shelf tools
lead with counting products. ShelfScan leads with baseline and
occupancy drift — how much the shelf has changed from its full
baseline — because a generic product counter cannot reliably name
packaged goods (see "Evidence, honestly" below). Counting is kept
secondary, single-class "product" only, no brand/SKU, never a stock
count.

Three decisions, each testable: (1) baseline drift is the primary
Gap signal, counting is secondary; (2) one class, "product," no
brand or SKU — trained on vending images, tested on real shelf
photos (MAE 7.0, n=5, estimate only); (3) conservative guards —
lighting and camera-move both fall back to Check, and alerts need
5 consecutive frames.

Two camera guards stop the commonest false alarms. A brightness
guard sends large lighting changes to Check shelf instead of Gap,
and a camera-move guard (phase correlation plus camera-shift
measurement) sends moving-camera footage to Check shelf instead
of Gap. A shelf that is genuinely emptied while the camera also
moves will conservatively report Check shelf, not Gap.

When ShelfScan is unsure, it says Check shelf — not Gap — so staff
are not sent to restock a shelf that is actually full. A false
restock trip is the cost this design is built to avoid.

## How it is built (brief)

- OpenCV 5.0.0, Python, FastAPI, vanilla HTML/CSS/JS dashboard.
  Server-side inference only; nothing runs in the browser.
- Pipeline: webcam frame → letterbox → YOLO26n ONNX (DNN output
  [1, 300, 6]) → IoU/centroid tracker → baseline drift as the
  primary shelf-state signal. Counting uses a separate single-class
  "product" model; see the technical report §12 for its details.
- AWS: full app on EC2 (t3.micro, eu-north-1, Docker image built
  from the repository Dockerfile, 399 MB, build passed on EC2).
  A Lambda demo-only endpoint is kept as a secondary link only.
- Tests: 39 passed locally.
  Pinned dependencies, SHA256-verified model download,
  reproducible run instructions in the README.

## Evidence, honestly

Shelf-state (drift) — this is what the product claims:

- Real photo, simulated gap (a real shelf photo with a whole row
  digitally removed, labelled as simulated, not a physical
  removal): single-shelf ROI, whole-row removal → **Gap,
  changed 0.4864**. A small central block alone was missed
  (Full, 0.0851). Gap is therefore observable, but only for a
  substantial removal inside one shelf area.
- Fixed-camera constructed video (real stills, Full then Gap):
  Full → Gap at the same 0.4864 change. This is the only
  Full-to-Gap video proof; it is constructed from stills, not
  a shop camera recording.
- 24 online shelf videos, 322 sampled frames: with no guard,
  214 of 298 post-baseline frames would have been Gap. With the
  phase guard alone, 50 frames were still false Gaps on slow
  pans. With phase plus shift guards, false Gaps fell to
  5 frames (1 momentary alignment, 4 person-occlusion frames).
  Moving footage is therefore reported as Check shelf, not Gap.
  No shop pilot and no fixed shop-camera footage exist yet.

Counting — an estimate, not an exact stock count:

- Single-class YOLO26n, trained on HoloSelecta (20 vending
  images, 807 boxes, one class 'product'), run in OpenCV 5
  DNN, single-tile, conf 0.10, latency 102–176 ms.
- Held-out real shelf stills, 5 countable photos, hand
  total 175, predicted 146, MAE 7.0, exact 0/5. Per photo:
  cookie 19/20, lemonade 91/88, wooden 14/16, soda 17/27,
  bleach 5/24 (white-on-white, worst case). A 6th photo was
  not reliably countable and was excluded, not counted.
- Generic COCO counting on the same 5 photos was MAE 18.4,
  with wrong labels (whole shelf as 'refrigerator', cookie
  tins as 'cell phone'). Classical alternatives did not beat
  it reliably (contour MAE 36.4, MSER MAE 29.6).
- No brand, SKU, labelling accuracy, exact stock count, or
  time-saved figure is claimed. Drift remains the primary
  gap signal; counting estimates how much is there.

## Challenges and what we learned

- Generic COCO labels fail on packaged goods: a whole shelf
  reads as "refrigerator", cookie tins as "cell phone", cans
  and bottles as "refrigerator" or "cup", and white bleach
  bottles score 0–2 at every threshold. The response was to
  change the headline from counting to shelf-state, not to
  hide the failure.
- Moving cameras break naive drift: slow pans kept phase
  correlation high enough to pass the first guard, so a
  second shift guard was added and validated on 24 videos.
- App Runner in eu-west-2 was unavailable for new customers
  and Lambda in eu-west-2 was region-blocked for this new
  account, so the full app was deployed on EC2 in eu-north-1
  instead. The Lambda link is kept only as a demo-only
  secondary link.

## Limitations and responsible use

- Fixed camera, one shelf, one area only. Multi-shelf, SKU,
  barcode, and POS work are out of scope.
- No shop pilot, no real physical removal pair, no
  person-occlusion handling yet. Occlusion can still flash Gap
  on a near-fixed camera.
- No login or rate limiting on the demo; session state is
  shared, so two judges or tabs can overwrite each other's
  baseline. Point the camera at the shelf only, not at staff,
  customers, or till areas. No facial recognition, no audio.
  Live frames are processed in memory and are not stored by
  default; only an explicit snapshot saves an image.
- EC2 ports 8000 and 22 are open to all addresses for demo
  only and will be restricted after judging. Free-tier cover
  through judging is not confirmed from billing data.
- No COOL and no Agentic Vision award is claimed.

## What's next

- Expand the boxed shelf training set (500–1000 boxed shelf
  images, with a held-out shelf test set) before claiming
  counting beyond the current MAE 7.0 estimate.
- Add person-occlusion handling so a person reaching for a
  product does not flash Gap.
- Run a real shop pilot with a fixed camera, a real
  before/after removal pair, and owner feedback on whether
  alerts are trusted and acted on — measuring three things not
  yet measured: facings caught before a customer reports them,
  manual shelf checks avoided, and false alerts per week.
  Until then, impact above is intended use, not measured
  outcome.

## Video

Current video (v4, counting + shelf state, 2:00, no burned-in
subtitles, natural voice, captions via YouTube):
https://www.youtube.com/watch?v=62QhywyJCFQ
Video shows counting as an estimate alongside drift; counting is
not a stock count.

## Code, architecture, and report

- Code: https://github.com/OlsOls4/opencv-hackathon-2026
- Technical report: docs/TECHNICAL_REPORT.md in the repository
- Architecture diagram: docs/architecture.svg in the repository
- Submission file: shelfscan-submission-v4.zip (Additional info)

## Built with

OpenCV 5, Python, FastAPI, YOLO, AWS EC2, AWS Lambda, Docker,
HTML, CSS, JavaScript
