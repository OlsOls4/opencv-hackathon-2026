# Real-photo drift pair — SIMULATED gap, not a real removal

**Honest label, read first:** the "Gap" images are a real Pexels shelf
photo (free licence, local only, never pushed to GitHub) with a
contiguous block of items digitally removed and filled with shelf
background. They are NOT photos taken after items were physically
removed. A real before/after removal pair is still untested.

## Method
- Baseline: `lemonade_bottles.jpg` (1920×1168, 88 items hand-counted in
  the earlier real-shelf evaluation) and, second photo,
  `soda_cans.jpg` (1920×1080, 27 items hand-counted).
- Gap fill (clone): the dark back-panel strip immediately above the
  block, stretched vertically to block height, Gaussian noise sigma 5,
  6 px edge feather. Price strip below the row is retained, as on a
  real empty shelf. One extra variant uses `cv2.inpaint` Telea r=15.
- Drift code: the exact app code, `Detector.set_baseline` /
  `occupancy_state` in `app/inference.py`, OpenCV 5.0.0, YOLO26n loaded
  but counting not used here. Thresholds: Full <0.10, Low <0.30,
  Gap ≥0.30, brightness guard >60 → Check shelf.
- Generated images (local only, do NOT push):
  `results/real_drift_pair/lemonade_gap_central.jpg`,
  `lemonade_gap_row.jpg`, `lemonade_gap_central_inpaint.jpg`,
  `soda_gap_central.jpg`. Visually verified: dark empty-shelf area,
  neighbouring bottles intact, price strip retained. The fill is
  visibly flat/dark on close inspection — it is a simulation, not a
  photorealistic removal.

## Results — default whole-image ROI (0.05, 0.10, 0.95, 0.90)

| Baseline → variant | changed_ratio | mean shift | State |
|---|---|---|---|
| lemonade → same image (control) | 0.0000 | 0.00 | Full |
| lemonade → central block, clone | 0.0385 | 3.41 | Full |
| lemonade → central block, inpaint Telea | 0.0397 | 3.05 | Full |
| lemonade → entire middle row, clone | 0.2021 | 20.79 | Low |
| soda → same image (control) | 0.0000 | 0.00 | Full |
| soda → front-row central block, clone | 0.1015 | 1.42 | Low |
| lemonade → brightness +80 (control) | 0.9554 | 70.17 | Check shelf |
| lemonade → brightness +20 (control) | 0.0000 | 19.87 | Full |

Controls behave correctly: identical = Full 0.0; +80 trips the Check
shelf guard, not a false Gap; +20 stays Full.

## Results — single-shelf ROI (the intended deployment: one shelf, one ROI)

| Baseline → variant | ROI | changed_ratio | mean shift | State |
|---|---|---|---|---|
| lemonade → central block, clone | middle row (0.02, 0.36, 0.98, 0.70) | 0.0851 | 7.54 | Full |
| lemonade → entire middle row, clone | middle row only | **0.4864** | 50.85 | **Gap** |
| soda → front-row central block, clone | front row (0.02, 0.30, 0.98, 0.82) | 0.1466 | 2.06 | Low |

## Key finding — and its limit
- **Gap IS observable on a real photo, but only with a single-shelf
  ROI.** With the default whole-image ROI, even removing a whole row
  only reaches Low (0.2021), because the change is diluted across
  three rows and because dark bottles are close in grayscale to the
  dark back panel (many removed pixels differ by <30 after the 21×21
  blur, so they never cross the threshold).
- A central block alone does NOT trigger even Low on the middle-row
  ROI (0.0851, just under the 0.10 Full boundary) — small gaps are
  missed by drift alone. That is a real sensitivity limit, not hidden.
- The full-row Gap (0.4864) sits below the brightness guard
  (mean shift 50.85 < 60), so it is reported as Gap, not Check shelf —
  but 50.85 is close to the guard; a brighter empty shelf could trip it.
- No threshold was changed for this test. Changing thresholds to
  chase this single simulated pair would be fitting to n=1 and is
  NOT done here.

## Limits
- n=2 photos, simulated gaps only, one removal size per photo (plus
  central vs full-row on lemonade). No real removal, no camera move,
  no gradual lighting change, no restock (re-baseline) pair.
- The cloned fill is darker/flatter than a true empty shelf, which
  may understate or overstate diff versus a real removal; direction
  (more removal → higher changed_ratio, Gap only at single-shelf ROI)
  is the claim, not an exact changed_ratio for real removals.
- Counting was not re-run here; the earlier real-shelf counting
  result (MAE 18.4, 0/5 exact) is unchanged and still the counting
  limit.
