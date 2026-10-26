# ShelfScan — video input evaluation (26 Oct 2026, local only)

## Verdict

**Video-input pipeline works end-to-end, but only for its intended
fixed-camera deployment.** Frame extraction, tiled/single-tile YOLO
detection, tracker, and baseline drift all run on real internet video
frames. The important correction from this work: on moving-camera
internet videos the shipped code previously reported a false **Gap**
on every frame after the baseline. A camera-move guard was added
(see §4); those videos now correctly report **Check shelf**, not Gap.
A true Full → Gap change was then proven on a fixed-camera video
constructed from real stills (§3). So: the system is complete for
fixed-camera video input, and it correctly refuses to claim a stock
change on moving-camera footage. It is **not** a stock-change detector
for arbitrary moving internet footage, and no such claim is made here.

## 1. Videos used — sources, licences, and a gap

Videos actually downloaded and evaluated (local only, in
`results/video_input/`, never pushed to GitHub):

| Video | Source page / file | Photographer / archive | Licence as shown | Duration / resolution / fps |
|---|---|---|---|---|
| getty_aisle | Getty preview: "Aisle in a supermarket", 0:19, file `aisle-in-a-supermarket.mp4` (640×640 preview link, actual file 768×432) | Getty Images (preview clip, ID 2174552700 visible as watermark in frame) | **NOT free-use.** Getty preview only. Used for local evaluation only, do NOT redistribute. | 19.06 s, 768×432, 23.98 fps, 457 frames |
| covid_empty_shelves | Covid-19 Archive item "Empty shelves during the beginning of the pandemic", Brooklyn College, file `82eea5cd9551aeb7ef685ab554da582d7426d560.mp4` | Covid-19 Archive / Brooklyn College collection | **Licence not stated on the item page.** Used for local evaluation only, do NOT redistribute. | 4.44 s, 686×1280 (portrait), 29.98 fps, 134 frames |

Content verified by viewing frames: getty_aisle is a moving pan past
a seasonal/Christmas-tree display with shelves on the left — not a
single fixed shelf, and the Getty watermark is visible. covid_empty_
shelves is a shaky handheld pan over genuinely near-empty shelves
(one bottle, a few tubs, mostly bare shelves).

**Pexels free-licence gap — CLOSED 26 Oct 2026:**
The two Pexels videos below were subsequently downloaded by a parent
browser task and re-run with `scripts/evaluate_video.py` (see §7).
They are free-licence, unlike the Getty/Covid videos above, but they
are still moving-camera footage, so the same Check-shelf conclusion
applies. Also noted, not yet downloaded: "Colorful Snack Aisle in a
Convenience Store", LayG Traveller, 3840×2160, 0:04 —
https://www.pexels.com/video/colorful-snack-aisle-in-a-convenience-store-28671127/
Do NOT present the two evaluated videos above as Pexels free-licence
videos. They are not.

## 2. Method

Script: `scripts/evaluate_video.py` (new, reusable). For each video:
baseline = frame 0 of that same video, default ROI
(0.05, 0.10, 0.95, 0.90), Detector.detect() (adaptive: single-tile
below 1200 px, 2×2 tiled above), Tracker(max_missed=5), and
Detector.occupancy_state() per sampled frame. Sampling: getty 1 fps
(20 frames), covid 2 fps (9 frames). Baseline-from-frame-0 means
drift here measures camera/scene change within that video, NOT a
stock change on one fixed shelf — that distinction is the whole
point of §4. A cross-baseline control (covid frames against the
lemonade full-shelf still) was also run and is labelled as such.

## 3. Results

Per-frame data: `results/video_input_eval.csv` (44 rows).
Summaries: `results/video_input_eval.json`.

### Before the fix (shipped code)
- getty_aisle: Full 1, **Gap 19**; mean changed_ratio 0.6354,
  mean shift only 0.1–28.4 (so the >60 brightness guard never fired).
- covid_empty_shelves: Full 1, **Gap 8**; mean changed_ratio 0.5788.
- Both are false Gaps: the camera moved, the stock did not change
  between frame 0 and frame 1 in any meaningful sense.

### After the fix (§4)
- getty_aisle: Full 1, **Check shelf 19**; mean detections 0.1/frame,
  mean latency 159.6 ms, unique track IDs 2, **track IDs persisted
  across sampled frames: 0/20**.
- covid_empty_shelves: Full 1, **Check shelf 8**; mean detections
  0.33/frame, mean latency 553.6 ms (2×2 tiled, 1280 px height),
  unique track IDs 3, **persisted: 0/9**.
- Cross-baseline (covid vs lemonade still): **Check shelf 9/9**,
  changed_ratio mean 0.69, phase response 0.011–0.025 — correctly
  refused as a different scene, not a Gap.

Detections on both internet videos are near-zero and spurious when
present (getty: "stop sign" once, "potted plant" once; covid:
"refrigerator", "bowl", "train"). This is the known COCO label-space
limit, not a video-specific bug: Christmas trees, packaged goods and
bare shelves have no COCO class. Tracker persistence of 0 is
therefore a detection-sparsity + moving-camera + 1–2 fps sampling
effect, not a tracker-code failure on its own — at 1–2 fps with a
moving camera, boxes do not overlap at IoU > 0.3, so no ID can
persist. The dashboard's ~300 ms frame rate would be needed for any
persistence claim, and even then only with repeated detections.

### Fixed-camera change proof (constructed, labelled as such)
`results/video_input/constructed_fixed_camera.mp4` (6 s, 10 fps,
built from real stills, NOT a found video): lemonade full photo for
0–3 s, then the real-photo simulated gap-row photo for 3–6 s,
single-shelf ROI (0.02, 0.36, 0.98, 0.70):
- t = 0, 1, 2 s: **Full**, changed 0.0, phase ~1.0, 12–14 detections.
- t = 3, 4, 5 s: **Gap**, changed 0.4864–0.4865, phase 0.183–0.184,
  24–25 detections, with many track IDs persisting across the
  fixed-camera frames (e.g. IDs 4, 5, 15, 19, 20, 7 across t = 3–5 s).
This proves the full video pipeline can report a true Gap when the
camera is fixed — the deployment the product is actually designed
for (one shelf, one camera, one ROI).

## 4. Code fix — camera-move guard

File changed: `app/inference.py` (`Detector.set_baseline` now also
stores the unblurred ROI gray; `Detector.occupancy_state` now
computes a phase-correlation response between baseline ROI and
current ROI, and returns `phase_correlation_response` and
`camera_shift_px`).

Guard: response < 0.10 → **Check shelf**, regardless of
changed_ratio. Measured locally, before choosing the threshold:
- Same scene: identical 1.0; +80 brightness 0.935; 5/20/50 px shift
  0.969/0.945/0.913; central gap 0.797–0.888; whole-row removal,
  default ROI 0.651, narrow single-shelf ROI **0.182**.
- Moved camera / different scene: internet video frames 0.008–0.071;
  different shelf photo −0.008.
Threshold 0.10 was chosen because an earlier 0.20 threshold tripped
on the true narrow-ROI row Gap (0.182). **The margin is narrow
(0.071 vs 0.182)** and is documented in the code as such: this guard
is conservative, not a solved camera-motion problem. It does not
align frames, it does not re-baseline, and it will not turn a moving
video into a stock measurement. Test added:
`tests/test_inference.py::test_camera_move_guard` (same frame → Full,
row Gap → Gap with response ≥ 0.10, different photo → Check shelf
with response < 0.10). Full suite: **20 passed**.

No other app code was changed. No video endpoint was added: the app
already processes one frame per `/api/frame` call, and
`scripts/evaluate_video.py` drives the same Detector/Tracker/
occupancy code frame by frame, so this evaluation is the shipped
pipeline, not a separate prototype.

## 5. Honest limits

- No real physical removal was found on video: no internet video
  shows the same fixed shelf before and after items are taken.
  The only true Gap on video here is the constructed stills video.
- No real shop pilot, no fixed shop camera footage, no gradual
  lighting change or restock/re-baseline on video.
- Getty preview is watermarked, low-resolution, and not free-use;
  covid clip is only 4.4 s, portrait, and shaky. Neither is a
  substitute for a fixed shop camera.
- Counting on video is not validated: there is no per-frame ground
  truth for either internet video, so no MAE/accuracy is claimed
  for video counting. Detection counts above are observed counts
  only.
- Latency is detection latency per sampled frame, not end-to-end
  dashboard latency, and covid tiled latency (~550 ms) would not
  sustain a 300 ms dashboard rate on high-resolution portrait
  frames without downscaling.
- The camera-move guard has a narrow threshold margin (see §4) and
  has not been tested on: slow pans (< 0.10 response but small
  shift), zoom, night/day change, or a shelf that is genuinely
  emptied while the camera also moves (that case will — correctly
  but conservatively — report Check shelf, not Gap).

## 6. Files

- `results/video_input_eval.csv` — 70 per-frame rows (44 earlier + 26 Pexels).
- `results/video_input_eval.json` — per-video summaries, now including
  `pexels_empty_shelves` and `pexels_beer_packs`.
- `results/video_input_eval.md` — this file.
- `scripts/evaluate_video.py` — reusable video evaluator.
- `results/video_input/getty_aisle.mp4`, `covid_empty_shelves.mp4`,
  `constructed_fixed_camera.mp4` — local only, do NOT push to GitHub.
- `results/video_input_frames/*.jpg` — sampled frame stills, local only.
- Code changed: `app/inference.py`, `tests/test_inference.py`.
  Nothing pushed to GitHub, no new demo video made, nothing
  submitted to Devpost, nothing deployed.

## 7. Pexels free-licence videos — evaluated 26 Oct 2026 (new)

Method, identical to §2: `scripts/evaluate_video.py`, baseline =
frame 0 of the same video, default ROI (0.05, 0.10, 0.95, 0.90),
Detector.detect() (1920 px → 2×2 tiled), Tracker(max_missed=5),
occupancy_state() per frame, sampling 1 fps. Baseline-from-frame-0
measures camera/scene change within that video, NOT a stock change
on one fixed shelf. No ground truth counts are claimed for either
video — detection counts below are observed counts only.

Files (local only, in `results/video_input_pexels/`, do NOT push
videos to GitHub):
- `pexels_supermarket_empty_shelves_cityxcape_3929080.mp4` —
  "Supermarket Empty Shelves", CityXcape, Pexels License: Free,
  https://www.pexels.com/video/supermarket-empty-shelves-3929080/
  — 12.69 s, 1920×1080, 29.97 fps, 380 frames, 7.7 MB.
- `pexels_beer_packs_gondola_shelves_dyon_siregar_11598349.mp4` —
  "Close up of Beer Packs on Gondola Shelves", Dyon Siregar, Pexels
  License: Free,
  https://www.pexels.com/video/close-up-of-beer-packs-on-gondola-shelves-11598349/
  — 12.50 s, 1920×1080, 24 fps, 300 frames, 8.9 MB.
- Sampled annotated frames: `results/video_input_pexels_frames/`
  (26 frames, local only).

### Results

| Video | Camera type | States (13 sampled frames) | Mean detections | Mean latency | Unique track IDs | Persisted frames |
|---|---|---|---|---|---|---|
| pexels_empty_shelves | Moving — pan to a different bay | Full 1, Check shelf 12 | 0.69/frame | 560.9 ms | 8 | 0/13 |
| pexels_beer_packs | Moving — horizontal pan across gondola | Full 1, Check shelf 12 | 2.62/frame | 561.9 ms | 30 | 1/13 |

Phase-correlation response, post-baseline frames (guard < 0.10 →
Check shelf):
- Empty shelves: 0.0039–0.0196, mean 0.0125. Changed_ratio
  0.2169–0.7094, mean 0.5273 (post-baseline). Without the guard
  this would have been a false Gap/Low on every post-baseline
  frame; with the guard it is correctly Check shelf on all 12.
- Beer packs: −0.0078–0.0539, mean 0.0033. Changed_ratio
  0.5821–0.8391, mean 0.7632 (post-baseline). Same conclusion:
  Check shelf on all 12 post-baseline frames.

Camera-shift estimates confirm movement, not a fixed camera:
empty shelves shows large vertical shifts (e.g. −400 to +375 px
between sampled frames); beer packs shows large horizontal shifts
(e.g. −825 to +808 px). Visual frame check agrees: empty shelves
frame 0 is a wide empty bay, frame at 6 s is a different bay with
a few jars/bottles; beer packs frame 0 is a close-up of Taiwan
beer packs, frame at 6 s is beer bottles in a fridge section.

Detections, observed only:
- Empty shelves: mostly 0–1/frame, total 9 over 13 frames:
  bottle 7, bus 1, oven 1 (see CSV). The near-empty shelves genuinely
  contain almost nothing detectable, so 0–1 is expected, not a
  counting failure on this video.
- Beer packs: total 34 over 13 frames, peaking at 8 at t = 5 s
  (bottle 6, wine glass 1, refrigerator 1). Bottles are detected
  when the pan pauses on them (t = 5–8 s: bottle 6, 4, 2, 3),
  but labels are still COCO-generic: beer packs become
  "refrigerator", "donut", "cake", "vase", "clock", "wine glass"
  as the camera moves. No per-frame ground truth, so no MAE is
  claimed.
- Tracker persistence is 0/13 (empty) and 1/13 (beer), same cause
  as §3: 1 fps sampling + moving camera + sparse/generic
  detections, so boxes do not overlap at IoU > 0.3 across samples.
  This is not a tracker-code failure on its own.

### Verdict for the Pexels videos

**The system works on these free videos exactly as designed for
its fixed-camera deployment: it runs end-to-end, and it correctly
refuses to claim a stock change on moving-camera footage.**
Both videos are moving-camera, so neither can prove a Full → Gap
stock change, and neither is a substitute for a fixed shop camera.
What they do add over the Getty/Covid videos is free-licence,
1080p, real shelf content (genuinely empty shelves, and real beer
packs/bottles) — usable as honest demo/evaluation footage with
their Pexels licences, unlike the Getty preview and the
unlicenced Covid clip. They do NOT change the §5 limits: no real
physical removal on video, no fixed shop camera footage, no video
counting accuracy claimed, latency ~561 ms at 2×2 tiled 1080p
would not sustain a 300 ms dashboard rate without downscaling,
and the camera-move guard margin remains narrow (see §4).
