# Detection improvement evaluation — 26 Oct 2026, before any new demo video

Question: can counting be significantly improved and validated before
a new demo video, or must the headline change to shelf-state only?

## Validation protocol

Same 5 countable real-shelf photos, same hand counts, no cherry-picking.
Hand counts are visual counts (multipack = 1 unit), NOT dataset ground
truth, and there are NO hand-drawn boxes — so box quality below is a
visual check, not an IoU score. COCO baseline is tiled 3x3, conf 0.35,
OpenCV 5.0.0, YOLO26n ONNX, run in the same environment.

Hand: bleach 24, lemonade 88, cookie 20, soda 27, wooden 16. Total 175.

## Method comparison (same 5 images)

| Method | bleach | lemonade | cookie | soda | wooden | Total | MAE | Bias | Exact |
|---|---|---|---|---|---|---|---|---|---|
| COCO conf 0.35 (baseline) | 0 | 61 | 4 | 7 | 21 | 93 | 18.4 | -16.4 | 0/5 |
| COCO conf 0.25 | 2 | 72 | 7 | 9 | 27 | 117 | 16.0 | -11.6 | 0/5 |
| COCO conf 0.50 | 0 | 52 | 0 | 2 | 11 | 65 | 22.0 | -22.0 | 0/5 |
| Contour (Canny + external) | 60 | 66 | 90 | 22 | 65 | 303 | 36.4 | +25.6 | 0/5 |
| MSER | 56 | 133 | 40 | 72 | 22 | 323 | 29.6 | +29.6 | 0/5 |
| SimpleBlob | 175 | 162 | 244 | 169 | 119 | 869 | 138.8 | +138.8 | 0/5 |
| Vertical edge peaks | 28 | 30 | 27 | 27 | 31 | 143 | 16.8 | -6.4 | 1/5 |
| Contour + large closing k=15/21/31 | 11/10/5 | 0/1/0 | 12/8/5 | 1/1/0 | 14/5/3 | — | 27.4/30.0/32.4 | -27.4/-30.0/-32.4 | 0/5 |
| Autocorrelation pitch, whole | 58 | 28 | 62 | 48 | 64 | 260 | 41.0 | +17.0 | 0/5 |
| Autocorrelation pitch, 3 bands | 188 | 105 | 184 | 175 | 184 | 836 | 132.2 | +132.2 | 0/5 |

Code for the classical methods: `app/agnostic_counting.py`, pinned by
`tests/test_agnostic.py` (22 tests pass in total, 4.24 s).

## Visual box check (5 real images)

- Contour boxes on lemonade: caps and label fragments, not whole
  bottles. Many boxes round a cap, a label patch, or a price tag.
- MSER boxes on cookie tins: text and graphics fragments inside
  tins, plus a few whole tins by accident and huge merged boxes
  spanning multiple tins. Not whole-item boxes.
- COCO boxes: object-like (bottles) when present, but labels are
  wrong: whole shelf as "refrigerator", cookie tins as "cell phone",
  cans/bottles as "refrigerator"/"cup". Bleach is 0-2 at every
  threshold (white-on-white, low contrast).
- Vertical peaks has no boxes at all: it counts column peaks, not
  items. Its MAE 16.8 is spurious — counts are 27-31 on every image
  regardless of hand count, and it collapses on multi-row shelves
  (lemonade 30 vs hand 88). It must NOT be reported as a counting win.

No classical method tested here produces boxes round whole items.

## Open-vocabulary detection (assessed, NOT run locally)

- YOLO-World / YOLOE: needs a CLIP text encoder ONNX plus a
  tokenizer matching that export, or the Ultralytics torch stack.
  This project deliberately runs OpenCV 5 DNN only; the earlier
  Ultralytics/torch wheel download stalled at 554 MB. Prompt-free
  YOLOE (4,585 classes) is the closest drop-in concept, but it still
  needs torch, weight download, ONNX export, prompt engineering
  ("bottle", "box", "can", "product on shelf" — multipacks and dense
  shelves are themselves a prompt-design task), and re-validation.
- GroundingDINO: 341-658 MB, transformer + BERT, cited CPU time
  about 1.8 s per image on an 8-thread Xeon — far above the 300 ms
  dashboard rate, and not an OpenCV DNN drop-in.
- Verdict: not feasible as a validated improvement before the
  06:45 GMT deadline, and no MAE improvement is claimed for it
  without a local run. It is a post-competition experiment, not a
  pre-video fix.

## Fine-tuning feasibility (estimate, NO training started)

What a real single-class "product" fine-tune would need:

- Annotations: boxes, not just counts. Current hand data is counts
  only, so the 5 real images need re-annotation (175 boxes), and
  HoloSelecta's 20 images (807 boxes, product+GTIN labels) would
  need conversion to a single "product" class. A credible set is
  hundreds of shelf images, not 5 — target 500-1000 images with
  boxes, plus a held-out shelf test set that is NOT used for tuning.
- Compute: YOLO26n training on CPU for hundreds of 640 px images
  is hours to days. On a GPU (e.g. a free Colab T4, if available,
  or a paid GPU instance) a 50-100 epoch run is plausibly 1-3 hours,
  plus ONNX export and OpenCV DNN re-verification, plus
  re-evaluation on the held-out set. No GPU account is connected
  here, and no Colab login is available in this session.
- Time to deadline: hours, not days. A rushed fine-tune on 5-25
  images would overfit those shelves, fail on new shelves, and
  could not be validated honestly before the deadline.
- Verdict: DO NOT start training now. Post-competition plan only:
  collect and box-annotate a larger shelf set, train single-class
  on GPU, validate on held-out shelves, then re-measure MAE.

## Go / no-go for claiming counting in the demo

NO-GO for counting as a headline claim. No method tested here
clearly beats COCO MAE 18.4 with correct boxes. COCO conf 0.25
(MAE 16.0) is numerically better but still has wrong labels,
worsens wooden bottles, adds a spurious "person" on soda cans,
and does not fix bleach (2) or cookie tins (7). It is not a
significant improvement, and it does not fix the demo visual problem.

RECOMMENDED headline change, already adopted for the demo plan:
shelf-state (baseline drift) only — Full / Low / Gap / Check,
with a drift overlay, not object boxes. Counting, if shown at all,
must be labelled secondary, unlabelled ("item", not a COCO class),
and never presented as a stock count. The drift signal is the
validated part: single-shelf ROI whole-row removal on a real
photo gives Gap 0.4864, and the fixed-camera constructed video
gives Full to Gap 0.4864, while the camera-move guards prevent
false Gaps on moving footage.
