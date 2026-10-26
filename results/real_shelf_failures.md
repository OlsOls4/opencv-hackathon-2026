# Real shelf photos — failures and limits

Method: app/inference.py `Detector.detect_tiled(img, 3, 3)`, conf 0.35,
OpenCV 5.0.0, YOLO26n ONNX. Annotated outputs in
`results/real_shelf_annotated/`. Source photos in
`results/real_shelf_images/` — LOCAL ONLY, never to be pushed to GitHub.

## Headline (countable n=5; half-empty shot excluded, see below)

MAE 18.4, bias −16.4, exact-match 0/5, within ±1: 0/5.
Total hand 175 vs total predicted 93. The model undercounts badly on
real shelves — except where tiling splits one item into several boxes.

## Hand counts — what they are and are not

These are my own visual hand counts from viewing each image, NOT
dataset ground truth. Counting rule: one saleable container = 1;
a shrink-wrapped multipack = 1 unit; items cut off to less than about
half, and blurred background shelves, are excluded. Uncertainty is
real, especially on dense shots:

- bleach_bottles.jpg — 24: distinct green caps visible, front row plus
  partially occluded back row. Occlusion makes this ±3.
- lemonade_bottles.jpg — 88: counted row by row (3 shelves), multipacks
  = 1. Stacked cans at top-right and edge bottles make this ±5.
- cookie_boxes.jpg — 20: 5 rows × 4 tins/boxes, all front-facing. Cleanest count.
- soda_cans.jpg — 27: front + back can rows on the upper shelf plus the
  partly visible lower row. Depth/blur makes this ±4.
- wooden_bottles.jpg — 16: 8 partly visible bottles/cans on the top
  shelf + 8 (6 bottles, 2 cans) on the main shelf.
- half_empty_shelves.jpg — NO hand count. This wide, dark, angled shot
  has distant small noodle packets, stacked trays and empty bays that
  cannot be counted reliably from the image alone. It is kept as a
  qualitative case only and excluded from MAE/bias. Inventing a number
  for it would fake precision.

## Per-image failures

- bleach_bottles.jpg (hand 24, pred 0): total miss. Large white
  bottles with green caps produced zero detections at conf 0.35 in
  any tile. White-on-white bottles against a bright background are
  effectively invisible to this COCO-trained detector — a reminder
  that "bottle" in COCO means a typical coloured/glass bottle, not
  any packaged liquid.
- lemonade_bottles.jpg (88 → 61): best relative result, still −27.
  Single bottles are mostly found (53 "bottle"), but the 8
  "refrigerator" boxes are false positives spanning whole shelf
  sections, and shrink-wrapped multipacks (Baon Pack, Lipton packs)
  are not counted as the units a shop would count. Dense rows also
  merge neighbouring bottles.
- cookie_boxes.jpg (20 → 4): near-total miss, wrong label. Square
  cracker/cookie tins have no COCO class, so the only detections are
  4 "cell phone" boxes on tin artwork. This is the COCO label-space
  limit in its purest form: the detector cannot name what it was
  never trained on, and its fallback guesses are unrelated objects.
- soda_cans.jpg (27 → 7): cans have no COCO class either. Only 4
  "bottle", 2 "refrigerator" and 1 "cup" were returned; most cans,
  including the whole blurred back row, were missed or merged.
  COCO has no crisps, chocolate, or cans classes — a shelf of cans
  is largely outside its vocabulary.
- wooden_bottles.jpg (16 → 21): the one overcount, and it is not a
  success. The annotated image shows tile-boundary splitting: the
  same bottle gets a box in two adjacent tiles (e.g. split neck/body
  boxes, "cup" fragments on bottle necks), plus a "refrigerator"
  false positive. Bottle-only count (17) is close to hand (16) by
  luck; the total is inflated by duplicate/fragment boxes.
- half_empty_shelves.jpg (pred 2): 1 "suitcase" + 1 "tv" on a shelf of
  noodle packets and empty bays. Small, dark, angled packets at
  distance are below reliable detection size even tiled, and the
  "gap" state this image should demonstrate is not something a
  COCO count can express at all.

## General limits (do not over-claim from this sample)

1. COCO label space: no classes for cans, crisps, chocolate,
   biscuits, noodle packets, bleach, or most packaged groceries.
   Counting via COCO labels therefore undercounts by design, and
   mislabels the rest (cell phone, refrigerator, suitcase, tv).
2. Dense packaged goods merge: neighbouring same-colour bottles/cans
   merge into one box, or one item splits across tiles.
3. Small sample, hand-counted: n=5 countable images, one photographer
   style per shot, no replicates, no live webcam footage. This is
   a smoke test of the counting claim, not a validated dataset.
   Do not quote MAE 18.4 as a general ShelfScan accuracy figure.
4. Implication (consistent with app/inference.py's own design):
   counting alone must not carry a "gap" claim. The primary signal
   remains baseline/occupancy drift; COCO counting is confirmatory
   only, and on real shelves it is weak confirmation.
