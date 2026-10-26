# Large video test set — ShelfScan evaluation (24 videos)

**Date:** 26 Oct 2026. **Method:** `scripts/evaluate_video.py`, baseline = frame 0
of the same video, default ROI, 1 fps sampling, adaptive tiling
(OpenCV 5.0.0, YOLO26n, conf 0.35). **Licence: evaluation only.**
All videos are Pexels License: Free as stated on their pages. Do NOT
redistribute the video files, do NOT push them to GitHub, do NOT claim
commercial rights. Video files live only in
`results/video_input_large/` (22 new) and `results/video_input_pexels/`
(2 previously downloaded, re-run here for uniform data).

**Important reading note:** baseline = frame 0 of the same video, so drift
here measures camera/scene change within that video, NOT a stock change
on one fixed shelf. No video in this set shows a real physical removal
on a fixed camera. A Gap on any of these videos is therefore a **false
Gap by construction** unless the camera was fixed and the shelf genuinely
emptied — which visual checks show did not happen (see §4).

## 1. Verdict — does the larger set change the prior verdict?

**Yes, in one important way, and no in the overall conclusion.**

- Prior verdict (4 videos: 2 Getty/Covid + 2 Pexels): the phase guard
  (phase < 0.10 → Check shelf) turned all moving footage into Check
  shelf. "Guard works" was the conclusion.
- On 24 videos the phase guard alone **does not** hold: it left **50
  false Gap frames** (16.8% of post-baseline frames). The failure mode is
  **slow pans**: repetitive shelf patterns keep phase correlation at
  0.18–0.60 while the camera drifts, so changed_ratio climbs past 0.30
  and Gap is claimed. Worst single video: local_convenience, 13/14
  post-baseline frames Gap under the phase guard alone.
- **Fix applied and verified in this task:** an additional camera-shift
  guard in `app/inference.py` — camera shift magnitude > 10 px →
  Check shelf. Calibration, measured not guessed: same-scene stills
  (identical, brightness +80/+20, simulated gap) measure ~0.0 px shift;
  near-fixed videos measure ≤ 4.9 px; slow-pan false Gap frames measure
  ≥ 14.7 px (except occlusion/momentary cases, §4). After the fix,
  Gap frames fall **50 → 5**, and moving-camera false Gap falls
  **46 → 1** (see §2). Full detection is unaffected (30 Full frames
  before and after), and the existing true-Gap unit test still passes.
- **Overall conclusion unchanged:** ShelfScan is a fixed-camera system
  only. Moving footage cannot prove a stock change, and the constructed
  fixed-camera stills video (`results/video_input/constructed_fixed_camera.mp4`)
  remains the **only** Full → Gap proof. Counting remains COCO-limited
  (§5). No shop pilot, no fixed shop camera in this set.

## 2. Aggregate — before and after the shift guard

| Metric | No guard (counterfactual*) | Phase guard only (before) | Phase + shift guard (after) |
|---|---|---|---|
| Videos / sampled frames | 24 / 322 | 24 / 322 | 24 / 322 |
| Post-baseline frames | 298 | 298 | 298 |
| Full | — | 30 | 30 |
| Low | — | 54 | 28 |
| Gap (post-baseline) | 214 would-be | 50 | **5** |
| Check shelf | — | 188 | 259 |
| False Gap on moving/slow-pan videos | — | 46 (15.4% of post-baseline) | **1 (0.3%)** |
| Mean latency (frame-weighted) | — | 683.9 ms | 680.9 ms (median 567.5 ms, max 1,476.7 ms) |
| Mean detections/frame | — | 5.52 | 5.52 (guard adds no inference cost) |

\* No-guard figure is a counterfactual from changed_ratio ≥ 0.30 alone,
ignoring the brightness guard (> 60 also forces Check). It is an upper
bound, not a measured run. The before/after figures are measured runs of
the same 24 videos with the same script; only `app/inference.py` changed.

Remaining 5 Gap frames after the fix (§4): 1 momentary alignment on a
moving cart journey (shift 2.6 px, phase 0.105 — just above the phase
threshold), and 4 person-occlusion/handling frames on near-fixed cameras
(2 jar shelves, 2 vitamins). The shift guard cannot catch those, because
the camera did not move — they are a separate failure mode, not a guard
tuning miss.

## 3. Per-video table (final guard: phase + shift)

Gap column is "before → after" post-baseline Gap frames. Phase/shift are
post-baseline means/maxima. Camera class is from phase/shift metrics
(§6), spot-checked visually only for the two near-fixed videos.

| Video | Downloaded res | Sampled | States (after) | Gap before→after | Mean phase | Max shift px | Mean det | Mean lat ms | Unique seen | Persisted frames |
|---|---|---|---|---|---|---|---|---|---|---|
| books_classroom | 1080x1920 | 15 | Full 1, Check 14 | 0→0 | 0.021 | 0.8 | 5.40 | 600.2 | 27 | 13 |
| bookshelves_living | 1080x1440 | 9 | Full 1, Check 8 | 0→0 | 0.005 | 200.3 | 18.22 | 644.2 | 115 | 7 |
| boxes_warehouse | 1080x1920 | 8 | Full 1, Check 7 | 0→0 | 0.076 | 83.7 | 1.75 | 556.6 | 3 | 7 |
| cart_journey | 1920x1080 | 15 | Full 1, Check 13, Gap 1 | 4→1 | 0.079 | 105.6 | 0.67 | 557.3 | 6 | 1 |
| cart_perspective | 3834x2160 | 11 | Full 1, Check 10 | 0→0 | 0.003 | 1652.2 | 9.91 | 1277.8 | 61 | 10 |
| chinese_supermarket | 1920x1080 | 6 | Full 1, Check 5 | 0→0 | 0.032 | 317.0 | 3.00 | 571.3 | 8 | 4 |
| fruit_veg_aisle | 1920x1080 | 26 | Full 1, Check 25 | 0→0 | 0.002 | 817.6 | 6.54 | 588.7 | 112 | 12 |
| fruit_veg_market | 1280x720 | 20 | Full 1, Check 19 | 4→0 | 0.079 | 404.3 | 10.25 | 586.6 | 60 | 19 |
| inventory_tablet | 1920x1080 | 13 | Full 1, Check 12 | 0→0 | 0.006 | 805.2 | 5.92 | 539.8 | 21 | 12 |
| inventory_warehouse | 1080x2048 | 20 | Full 1, Check 19 | 0→0 | 0.076 | 822.3 | 0.60 | 1256.3 | 12 | 0 |
| jar_shelves_portrait | 1080x1920 | 12 | Full 1, Low 9, Gap 2 | 2→2 | 0.491 | 0.1 | 7.08 | 564.5 | 18 | 11 |
| library_book | 1920x1080 | 11 | Full 1, Check 10 | 0→0 | 0.018 | 610.2 | 2.91 | 625.5 | 8 | 10 |
| local_convenience | 1920x1080 | 15 | Full 1, Check 14 | 13→0 | 0.479 | 127.4 | 6.40 | 563.4 | 29 | 14 |
| man_buying_portrait | 1080x1920 | 10 | Full 1, Low 1, Check 8 | 8→0 | 0.600 | 89.3 | 4.00 | 623.3 | 8 | 9 |
| people_market | 1920x1080 | 10 | Full 1, Check 9 | 0→0 | 0.000 | 268.8 | 13.60 | 590.2 | 70 | 9 |
| pexels_beer_packs | 1920x1080 | 13 | Full 1, Check 12 | 0→0 | 0.003 | 825.3 | 2.62 | 565.6 | 30 | 1 |
| pexels_empty_shelves | 1920x1080 | 13 | Full 1, Check 12 | 0→0 | 0.013 | 400.4 | 0.69 | 618.1 | 8 | 0 |
| snack_aisle | 1920x1080 | 5 | Full 1, Check 4 | 0→0 | 0.045 | 131.6 | 1.60 | 575.5 | 3 | 3 |
| warehouse_cart | 2048x1080 | 21 | Full 4, Check 17 | 7→0 | 0.194 | 98.2 | 5.10 | 1175.8 | 11 | 20 |
| warehouse_organizing | 1080x1920 | 21 | Full 1, Check 20 | 0→0 | 0.110 | 80.5 | 3.86 | 553.8 | 8 | 20 |
| woman_juice_aisle | 1920x1080 | 6 | Full 1, Check 5 | 3→0 | 0.196 | 71.1 | 5.17 | 549.5 | 9 | 5 |
| woman_local_grocery | 1920x1080 | 16 | Full 4, Low 3, Check 9 | 3→0 | 0.235 | 32.0 | 9.06 | 536.8 | 26 | 15 |
| woman_shopping_portrait | 1080x1920 | 10 | Full 1, Low 2, Check 7 | 4→0 | 0.266 | 29.3 | 4.20 | 588.4 | 8 | 9 |
| woman_vitamins | 1920x1080 | 16 | Full 1, Low 13, Gap 2 | 2→2 | 0.268 | 4.9 | 4.44 | 523.9 | 11 | 15 |

Full frames above the 24 baselines (warehouse_cart 4, woman_local_grocery
4) are return-to-baseline-view frames, not errors: the camera came back
to a view matching frame 0, and the shift guard correctly left them Full.

## 4. Failure modes, ranked

1. **Slow pan (fixed by shift guard).** Phase stays 0.18–0.60 on
   repetitive shelves while shift grows to 29–127 px. Before: 46 false
   Gap frames on moving/slow-pan videos. After: 1. Examples:
   local_convenience 13→0, man_buying_portrait 8→0, warehouse_cart 7→0.
2. **Person occlusion / product handling on a near-fixed camera (NOT
   fixed).** The camera does not move (shift 0.0–4.9 px), but a person
   steps in front of the shelf or takes a product in hand, so
   changed_ratio passes 0.30. Visually verified from extracted frames:
   jar_shelves t=5 — woman reaches to the top shelf, her body occludes
   most of the shelf (Gap, changed 0.359, shift 0.1 px); woman_vitamins
   t=14 — woman holds a bottle in front of the shelf while comparing
   products (Gap, changed 0.301, shift 4.9 px). Mitigating factor: the
   dashboard alert needs 5 consecutive Gap/Low frames, and these are
   2-frame transients, so they would not raise an alert in the live app
   — but the state display would still flash Gap. A real fix needs
   person-box masking or Gap persistence after the person leaves; that
   is out of scope for this task and is not claimed.
3. **Momentary alignment on moving footage (NOT fixed).** cart_journey
   t=8: shift 2.6 px, phase 0.105 (just above the 0.10 threshold),
   changed 0.413 → Gap. One frame out of 298 post-baseline.
4. **COCO label-space counting limit (unchanged).** See §5.
5. **High-res / portrait latency.** Mean latency 680.9 ms (median
   567.5 ms) at 1 fps sampling is fine for evaluation, but it would NOT
   sustain the 300 ms dashboard rate on 1080p+ tiled frames without
   downscaling. Slowest: cart_perspective (3834x2160) 1,277.8 ms,
   inventory_warehouse (1080x2048) 1,256.3 ms, warehouse_cart
   (2048x1080) 1,175.8 ms. No crashes on portrait, high-res, or short
   clips (shortest: snack_aisle 4.3 s, 5 frames; chinese_supermarket
   5.7 s, 6 frames).

## 5. Counting on video — no MAE claimed

No per-frame ground truth exists for these videos, so **no video
counting MAE is claimed**. Detection sparsity (final guard run):
mean 5.52 detections/frame, 32/322 frames (9.9%) with zero detections.
Top labels across all frames: person 567, bottle 232, orange 201,
apple 201, book 138, refrigerator 100, potted plant 99, bowl 49,
train 33, banana 22. The same COCO label-space problem as the still
evaluation applies: beer packs become "refrigerator"/"donut"/"cake",
shelf goods become "bottle"/"orange"/"apple" generically, and a
"train" fires on warehouse racking. Tracker persistence
(226/322 frames with a persisted track) is meaningful only on
near-fixed videos (e.g. jar 11/12, vitamins 15/16, warehouse_organizing
20/21); on moving videos it collapses (cart_journey 1/15, beer packs
1/13, empty shelves 0/13), as expected — the tracker cannot persist
across a moving camera and 1 fps sampling.

## 6. Sources, camera type, and download notes

Camera type is classified from phase/shift metrics: moving = mean
post-baseline phase < 0.10; slow-pan/moving = phase ≥ 0.10 with max
shift > 25 px; near-fixed = shift ≤ 4.9 px with high phase (visually
spot-checked). All pages state Pexels License: Free.

| Video | Source (Pexels) | Author | Page dims / fps | Downloaded res / duration | Camera |
|---|---|---|---|---|---|
| snack_aisle | 28671127 | LayG Traveller | 3840x2160 / 60 | 1920x1080, 4.3 s | moving |
| woman_local_grocery | 29814585 | Aamir Somewhere | 3840x2160 / 60 | 1920x1080, 15.6 s | slow-pan |
| woman_juice_aisle | 29846453 | Aamir Somewhere | 3840x2160 / 60 | 1920x1080, 5.2 s | slow-pan |
| woman_shopping_portrait | 6097040 | Laura James | 2160x3840 / 23.98 | 1080x1920, 10.0 s | slow-pan |
| warehouse_cart | 7019234 | cottonbro studio | 4096x2160 / 25 | 2048x1080, 20.1 s | slow-pan |
| man_buying_portrait | 7125847 | Michael Burrows | 2160x3840 / 23.98 | 1080x1920, 10.0 s | slow-pan |
| cart_journey | 29068393 | Glimpses Into Reality | 1920x1080 / 30 | 1920x1080, 15.0 s | moving |
| jar_shelves_portrait | 5453398 | Leeloo The First | 1080x1920 / 29.97 | 1080x1920, 11.9 s | near-fixed (kitchen shelves) |
| woman_vitamins | 5103996 | Gustavo Fring | 3840x2160 / 29.97 | 1920x1080, 16.0 s | near-fixed |
| warehouse_organizing | 6169087 | Tima Miroshnichenko | 2160x3840 / 25 | 1080x1920, 20.2 s | slow-pan |
| inventory_warehouse | 7018670 | cottonbro studio | 2160x4096 / 25 | 1080x2048, 19.5 s | moving |
| boxes_warehouse | 6170316 | Tima Miroshnichenko | 2160x3840 / 25 | 1080x1920, 7.6 s | moving |
| fruit_veg_market | 15645011 | Atlantic Ambience | 1920x1080 / 25 | 1280x720, 19.1 s | moving |
| people_market | 2016738 | Carlos Prieto | 1920x1080 / 23.98 | 1920x1080, 9.5 s | moving |
| fruit_veg_aisle | 992683 | jessica politi | 1920x1080 / 25 | 1920x1080, 25.5 s | moving |
| bookshelves_living | 10822607 | Jordann Player | 1440x1920 / 29.97 | 1080x1440, 9.0 s | moving (living-room bookshelves) |
| inventory_tablet | 4292901 | Tiger Lily | 3840x2160 / 50 | 1920x1080, 12.6 s | moving |
| cart_perspective | 29376327 | Dubang chang | 3834x2160 / 30 | 3834x2160, 10.8 s | moving |
| books_classroom | 8363896 | RDNE Stock project | 1080x1920 / 30 | 1080x1920, 15.0 s | moving |
| library_book | 6550147 | Tima Miroshnichenko | 3840x2160 / 25 | 1920x1080, 11.0 s | moving |
| chinese_supermarket | 34813666 | LayG Traveller | 3840x2160 / 59.94 | 1920x1080, 5.7 s | moving |
| local_convenience | 31494166 | Aamir Somewhere | 3840x2160 / 60 | 1920x1080, 14.6 s | slow-pan |
| pexels_empty_shelves | 3929080 | CityXcape | 1920x1080 / 29.97 | 1920x1080, 12.7 s | moving |
| pexels_beer_packs | 11598349 | Dyon Siregar | 1920x1080 / 24 | 1920x1080, 12.5 s | moving |

Download notes (Pexels download endpoint
`https://www.pexels.com/download/video/<id>/?fps=<exact>&h=<h>&w=<w>`,
curl with browser User-Agent and Pexels Referer):
- Exact FPS is required: 28671127 failed at fps=30 (0 bytes) and
  succeeded at fps=60; 4292901 failed at the page FPS 50 and succeeded
  at fps=25 — the served file variant does not always match the page.
- Non-16:9 sources need matching aspect: 7019234 (4096x2160) failed at
  1920x1080 and succeeded at 2048x1080; 29376327 (3834x2160) only
  succeeded at its original dimensions; 15645011 was served as
  1280x720 despite a 1920x1080 request.
- **Failed and excluded:** 36074343 (Stock Clerk Organizing Grocery
  Store Shelves, Circuit Occidental, 3840x1728, 0:09, fps 30) — the
  download endpoint returned 0 bytes for every variant tried (fps
  25/29.97/30/60; 1920x864, 3840x1728, 1920x1080, 1280x576). It was not
  evaluated and is not counted in the 24.

## 7. Code change and tests

- `app/inference.py`, `occupancy_state`: added the shift guard
  (shift magnitude > 10.0 px → Check shelf, in addition to phase <
  0.10) and a `camera_shift_magnitude_px` return field. The guard
  comment records the measured calibration (same-scene ~0 px,
  near-fixed ≤ 4.9 px, slow-pan false Gap ≥ 14.7 px).
- `tests/test_inference.py`: added `test_slow_pan_shift_guard`
  (30 px shifted real shelf photo → Check shelf with shift > 10 px;
  identical frame → Full).
- **Test suite: 21 passed** (20 before + 1 new), including the existing
  true-Gap test (single-shelf ROI whole-row removal still Gap, shift
  ~0 px). No other files changed. Code changes are local only in this
  task — no GitHub push, no Devpost change, no deploy, no demo video
  made, per the task constraints.

## 8. Honest limits

- No shop pilot, no fixed shop camera, no real physical removal on
  video. The only Full → Gap proof remains the constructed
  fixed-camera stills video.
- Camera classification is metric-based (phase/shift), with visual
  spot-checks only for the two near-fixed videos; other videos were not
  watched end-to-end by a person.
- The 10 px shift threshold is calibrated on this set plus same-scene
  stills. It is not validated on an independent fixed-camera set, and
  a violently shaking fixed camera could exceed 10 px and be forced to
  Check shelf (conservative failure, not a false Gap).
- Occlusion false Gaps (4 frames) remain unfixed; person-box masking or
  Gap persistence is future work, not claimed here.
- No video counting MAE is claimed (no per-frame ground truth; no
  video had a clear countable frame hand-counted for this report).
- Latency is evaluation latency at 1 fps sampling, not dashboard
  frame rate; ~681 ms mean would not sustain 300 ms on 1080p+ tiled
  frames without downscaling.
- Video files are evaluation-only and must not be redistributed or
  pushed to GitHub.

## Files

- This report: `results/video_input_large_eval.md`
- Per-frame rows (final guard, 322 rows): `results/video_input_large_eval.csv`
- Per-video before/after summaries, aggregates, sources:
  `results/video_input_large_eval.json`
- Before-guard per-video JSONs: `results/video_input_large/eval_json/`
- After-guard per-video JSONs: `results/video_input_large/eval_json_after/`
- Video files (local only, never push):
  `results/video_input_large/*.mp4` (22) and
  `results/video_input_pexels/*.mp4` (2 re-run)
- Aggregation helper: `results/video_input_large/aggregate.py`
- Spot-check frames (local only): `results/video_input_large/frames_check/`
