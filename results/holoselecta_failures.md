# HoloSelecta first-20 — failure analysis (counting only)

Headline: YOLO26n COCO counting systematically undercounts dense vending
products. This is NOT a shelf result and NOT labelling accuracy.

## Metrics (20 images, run locally, OpenCV 5.0.0, YOLO26n, conf 0.35)
- GT boxes total: 807 (26–45 per image, mean 40.35)
- Predicted total: 46 (0–9 per image, mean 2.3)
- MAE: 38.05 | Exact match: 0/20 | Within ±1: 0/20 | Bias: −38.05
- Latency: mean 163.6 ms, median 142.4 ms — speed is fine; detection is the failure.
- Predicted labels across all 20 images, total only: refrigerator 19, bottle 27.
  No other COCO label fired. 4 images predicted 0, 16 predicted ≤2.

## Top 5 failures (by absolute error; annotated copies in results/holoselecta_annotated/)
1. IMG_20190430_110010.jpg — GT 45, PRED 1 (refrigerator), err −44, 109.3 ms
2. IMG_20190402_110254.jpg — GT 43, PRED 0, err −43, 101.7 ms
3. IMG_20190430_105805.jpg — GT 43, PRED 0, err −43, 111.0 ms
4. IMG_20190430_105808.jpg — GT 44, PRED 1 (refrigerator), err −43, 137.6 ms
5. IMG_20190430_110153.jpg — GT 43, PRED 0, err −43, 118.7 ms
(Also −43 on IMG_20190430_110329.jpg, GT 45, PRED 2.)

## Causes, grounded in the run and the images
- Wrong label space: GT names are product + GTIN strings (e.g.
  redbull___33__90162909, caprisun_multivitamin__20__4000177605004).
  COCO has no class for crisps, chocolate bars, cans, or snack packs, so
  most products can never be counted by this model, whatever the threshold.
- Whole-machine merge: the model fires "refrigerator" for the vending
  machine itself (19 times across 20 images), swallowing the products inside it.
- Scale: source images are up to 3456×4608; letterboxing to 640×640 shrinks
  dense, small packaged goods far below reliable COCO detection size.
  Larger bottles are the only products regularly detected (27 bottle boxes).
- Glass, glare, and spiral coils occlude or split products; several GT boxes
  are for items behind glass or partly hidden by coils.
- Best case still fails: 20190125_114246.jpg — GT 37, PRED 9
  (1 refrigerator + 8 bottles), err −28. Even the best image misses all
  snacks, cans, and most bottles.

## What this does NOT show
- No product labelling accuracy is claimed or measurable here: COCO labels
  cannot match the 109 GTIN products.
- No baseline-drift / Full-Low-Gap state result: these are single stills
  with no before/after pair, so ShelfScan's primary signal is untested by
  this dataset.
- Not a shelf proxy: these are vending machines, not open shelves. A shelf
  result still needs Olly's staged shelf photos with hand counts.
- Implication for the submission: report this honestly as a counting
  failure on dense packaged goods, and do NOT present YOLO count as the
  primary shelf signal. Baseline/occupancy drift remains the primary claim,
  and it still needs its own before/after test.

## Scope note (judge review, 26 Oct 2026)
- This file covers single-tile counting only (pred 46 / GT 807). No tiled
  label breakdown, no precision/recall/F1 at IoU≥0.50, no latency p95,
  and no video count-stability result exists yet, although
  docs/EVALUATION.md lists them. Do not quote a labelling accuracy or
  a tiled failure ranking from this file.
