# Counting evaluation — ShelfScan, 26 Oct 2026

User decision: counting IS wanted, as a priority. This replaces the
earlier NO-GO verdict for counting as a headline, with the caveats below.
No video was made, nothing was pushed to GitHub, nothing was submitted.

## Validation protocol
Same 5 real shelf photos, same hand counts, no cherry-picking.
Hand (visual counts, multipack = 1 unit, NOT dataset ground truth):
bleach 24, lemonade 88, cookie 20, soda 27, wooden 16. Total 175.
Real shelf photos were NEVER trained on in any method below.
Box quality is a visual check of the annotated images, not an IoU score
(no hand-drawn boxes exist for these 5 photos).

## Method comparison (same 5 images)

| Method | bleach | lemonade | cookie | soda | wooden | Total | MAE | Bias | Exact |
|---|---|---|---|---|---|---|---|---|---|
| COCO YOLO26n, tiled 3x3, conf 0.35 (old baseline) | 0 | 61 | 4 | 7 | 21 | 93 | 18.4 | -16.4 | 0/5 |
| COCO, conf 0.25 | 2 | 72 | 7 | 9 | 27 | 117 | 16.0 | -11.6 | 0/5 |
| FODUU YOLOv8 shelf, tiled, conf 0.10 (pretrained, HF) | 12 | 84 | 23 | 8 | 14 | 141 | 8.0 | -6.8 | 0/5 |
| FODUU, tiled, conf 0.25 | 7 | 73 | 13 | 7 | 6 | 106 | 13.8 | -13.8 | 0/5 |
| Holo-trained YOLO26n, tiled 3x3, conf 0.10 | 14 | 100 | 17 | 25 | 26 | 182 | 7.4 | +1.4 | 0/5 |
| Holo-trained, single-tile, conf 0.10 (Ultralytics) | 7 | 102 | 22 | 18 | 18 | 167 | 8.8 | -1.6 | 0/5 |
| **Holo-trained, single-tile, conf 0.10 (OpenCV ONNX, app/product_counter.py)** | **5** | **91** | **19** | **17** | **14** | **146** | **7.0** | **-5.8** | **0/5** |
| Holo-trained, single-tile, conf 0.25 | 1 | 61 | 16 | 5 | 8 | 91 | 16.8 | -16.8 | 0/5 |
| Holo-trained, tiled, conf 0.35 | 1 | 57 | 3 | 3 | 3 | 67 | 21.6 | -21.6 | 0/5 |

Best counting method: Holo-trained single-class model, OpenCV ONNX,
single-tile, conf 0.10. MAE 7.0 vs COCO 18.4 — a 2.6x improvement,
with no COCO wrong labels (every box is just "product").

## What the Holo-trained model is
- Base: YOLO26n pretrained, fine-tuned 20 epochs, imgsz 640, batch 4, CPU.
- Data: HoloSelecta 20 vending images, 807 Pascal VOC boxes converted
  to ONE class 'product', tiled 2x2 (64 train tiles / 1026 tile boxes,
  16 val tiles / 241 boxes). Train/val split by image (last 4 held out).
- Held-out vending val: mAP50 0.778, mAP50-95 0.486, precision 0.80,
  recall 0.68 at 20 epochs. Training took ~17 min on this 2-CPU VM.
- Weights: models/product_yolo26n.onnx (9.4 MB, local only, NOT
  committed — same rule as the COCO ONNX, fetched/trained not committed).
  Code: app/product_counter.py, tests/test_product_counter.py.
  Training script: results/counting_work/train_product.py,
  dataset: results/counting_work/dataset/ (data.yaml, images/labels).
- Latency: ~102-176 ms per image, single-tile, OpenCV 5.0.0 CPU —
  inside the ~300 ms dashboard rate. Tiled inference is 630-4700 ms
  and is NOT used for this counter.

## Box visual check — the decisive caveat
- Single-tile, conf 0.10: cookie tins are almost perfect whole boxes
  (rows 2-5), lemonade bottles are mostly whole bottles with some
  duplicates on the dense top row. These two are demo-usable.
- Tiled, conf 0.10: count is slightly better (MAE 7.4) but boxes are
  FRAGMENTS — label patches, cracker graphics, bottle necks, price
  tags — because tiles cut items. Do NOT show tiled boxes in a video.
- Bleach: 5/24 (OpenCV) / 7/24 (Ultralytics single) — white bottles on
  white, still the worst case. Do NOT use bleach as a demo hero.
- Soda: 17/27, wooden: 14/16 — usable as a count, not as a clean
  box visual (duplicates and partials on dark/occluded rows).
- No box is labelled with a wrong product name any more: the only
  label is "product". That fixes the v2 "cell phone / refrigerator"
  problem, but it does not fix fragment/duplicate boxes.

## Pretrained models searched (route 1)
Full shortlist: ~/workspace/shelfscan-model-shortlist.md (search agent).
- FODUU YOLOv8 shelf (Hugging Face, 22 MB .pt, 43 MB ONNX, classes
  empty/product, licence NOT stated): tested here on the 5 clean
  photos, MAE 8.0 at conf 0.10, soda 8/27 — good, but worse than the
  Holo-trained model, and its licence is unstated, so it is NOT the
  recommended counter.
- SKU-110K-trained YOLOv8 (albertferre shelf-product-identifier,
  vmc-7645 YOLOv8-retail): no verified direct weights download found;
  SKU-110K itself is academic/non-commercial only and 13.6 GB.
  RF-DETR: COCO-only pretrained, no shelf checkpoint. YOLO-World:
  needs CLIP embeddings, not an OpenCV DNN drop-in. Roboflow
  Universe models: weights not downloadable (hosted API only).

## GPU route estimate (route 2, for finishing counting properly)
- This Holo run needed no GPU: 17 min CPU for 20 epochs on 64 tiles.
- A proper finish would be: SKU-110K (or Roboflow shelf data, CC BY)
  + HoloSelecta + hand-boxed real shelf photos (175 boxes for the
  5 photos, plus more shelves), trained on a free Colab T4 if a
  login is connected (none is connected here) or a paid GPU.
  Estimate: Holo-scale on T4 is minutes; SKU-110K full (11,762 imgs)
  is plausibly 3-6 hours for 20 epochs on a T4, plus ONNX export
  and held-out re-evaluation. Do NOT claim that run without doing it.
- The cheapest next step that would most improve this model is
  NOT more epochs on vending: it is adding boxed real shelf photos
  (different shelves, bottles, cans, boxes) to training, then
  re-validating on a held-out shelf that was never trained on.

## Counting headline recommendation
Counting CAN now be claimed, but only in this honest form:
- "Counts products on one shelf (single class 'product', no brand
  or SKU names), about ±7 items per photo on 5 held-out shelf
  photos (hand total 175, predicted 146, MAE 7.0, exact 0/5),
  best on clear bottle/box rows, weakest on white-on-white
  bottles and occluded cans."
- Do NOT claim: a stock count, exact inventory, SKU/brand
  identification, or accuracy on shelves unlike the 5 tested.
- Demo video: show single-tile product boxes on cookie/lemonade
  (the clean visuals), show the count as an estimate, and keep
  shelf-state (drift: Full/Low/Gap) as the primary Gap signal —
  drift is what proves a shelf is empty, counting is what
  estimates how much is there.
- Tests: 23 passed (was 22, +1 product counter test pinning the
  5 counts above). Nothing pushed, nothing submitted, per task.
