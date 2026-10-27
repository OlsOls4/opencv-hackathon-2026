# Evaluation — original plan, now superseded by the run results in docs/TECHNICAL_REPORT.md §7/§11 (COCO legacy) and §12 (single-class product counting, MAE 7.0, n=5)

Note: this plan predates the evaluation run; do not read its "not yet run" framing as current — the results are in the technical report.

Freeze code, dependencies, model, threshold, and sample lists before running.
Use scripts/evaluate.py; never hand-edit results/eval_results.json.

Slimmed set for ~11 hours (per judges):
- HoloSelecta (CC BY 4.0, vending-domain transfer, not a shelf proxy)
- Olly's staged shelf: minimum 5 shots, ideally 10, with hand-counted ground truth
- SKU-110K: appendix stress test only, labelled "expected to fail for dense
  small items", single class only — never label accuracy
- Drop RPC and MVTec D2S until licences verified; drop Humans in the Loop
  if its form gate blocks download, and note that honestly.

Metrics: counting MAE, MAPE (true>0), exact-match, within ±1, bias;
detection precision/recall/F1 at IoU>=0.50 at a single threshold;
labelling accuracy only where labels exist; latency median + p95 and FPS,
stating local vs AWS; video count stability; alert metrics (false Gap
alerts on static shelf, time to alert after removal, lighting/camera-bump behaviour).

Document at least 5 failures with annotated image + cause + mitigation:
occlusion, glare, similar packaging, low light, motion blur, perspective,
dense merging/splitting, empty-gap false positives, open-world labelling limit.

If no Olly footage is delivered: report "evaluated on public stills only;
live webcam evaluation not completed" — do not claim a tested webcam demo.
