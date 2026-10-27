# ShelfScan — Submission checklist

- Repo: https://github.com/OlsOls4/opencv-hackathon-2026
- Deadline: 27 Oct 2026 06:45 GMT
- Status as of 27 Oct 2026 05:27 GMT: SUBMITTED to Devpost
  (submission 1266470, https://devpost.com/software/shelfscan-tm39q7,
  5/5 steps, video v4 live https://www.youtube.com/watch?v=62QhywyJCFQ,
  submission file shelfscan-submission-v4.zip). Deadline 27 Oct 2026
  06:45 GMT.
- Judge review history: round 1 average 4.58/10, round 2 4.78/10, final
  panel 5.1/10, later panel Technical 5.8/Cloud 5.0, UX 6.5/Docs 6.5,
  Innovation 4.5/Impact 3.5. Since then: full app live on EC2 (Docker
  399 MB, build passed), 24-video guard validation (false Gaps
  50 → 5), single-class counting wired in (MAE 7.0, n=5), 39 tests
  passed. Video v4, submission ZIP v4, thumbnail and 7-image gallery
  all live on Devpost.
- This file is local-only, ready for a bulk `push_files` (excluding `.github/workflows/test.yml` and `models/yolo26n.onnx`). Do NOT push it via single-file `create_or_update_file`.
- COOL and Agentic Vision are optional and are NOT claimed.

## Requirement table

| Requirement | Status | Evidence | Owner | Exact remaining human step for Olly |
|---|---|---|---|---|
| Technical report: problem, users, architecture, OpenCV 5 implementation, AWS deployment, evaluation, limitations, responsible use | DONE | `docs/TECHNICAL_REPORT.md` — covers all sections; full app live on EC2, evaluation: 5 held-out real shelf photos, MAE 7.0, simulated Gap 0.4864, no shop pilot, no physical pair | Muse / Olly | Keep EC2 live through judging. |
| Judge-accessible code repo, pinned dependencies, clear build / deployment / test instructions | PARTIAL | Repo pushed 39/40 files 26 Oct 2026 (plus later bulk pushes — verify current count before submitting); `requirements.txt` pins `opencv-python-headless==5.0.0.93` and all other deps; `README.md` gives venv, install, model-download, smoke-test, uvicorn and Docker commands; `models/download_model.py` fetches ONNX (SHA256-verified) instead of committing it; `tests/` + `scripts/smoke_test.py` | Muse (file ready) / Olly (repo permissions) | For full CI only: manually add `.github/workflows/test.yml` in GitHub, or grant workflows permission — the API blocks workflow files without it. Docker-test the `Dockerfile` on the deploy machine (Docker was unavailable in this VM, so it is NOT build-tested). Open: Dockerfile untested; CI workflow not on GitHub; `results/latency.md` not yet written; Lambda demo code not in repo. None of these is claimed as done. |
| Architecture diagram showing OpenCV 5 and AWS components | PARTIAL (diagram text is stale: it still says Lambda-only + local app, not EC2) | `docs/architecture.svg` + `docs/architecture.md` — text must be updated to EC2 full app first, Lambda demo-only second, before it is relied on as the deployed architecture | Muse | Update architecture.md/svg to EC2-first before final judging. Do not submit the old Lambda-only text as the deployed architecture. |
| Working web endpoint OR arranged live screen-share | DONE (full app, EC2) | Full app live on EC2: http://16.171.250.54:8000 — /health OpenCV 5.0.0, /api/demo Low 0.216, verified from outside AWS 26 Oct 2026. Lambda demo-only link kept as secondary only. | Muse | Keep EC2 running through judging (27 Oct–10 Nov 2026), then stop/terminate and restrict ports 8000/22. Free-tier cover through judging is not confirmed from billing. |
| ≤5-minute public/unlisted video: team, app working, architecture, principal results | DONE (v4 live) | v4 live, unlisted, 2:00: https://www.youtube.com/watch?v=62QhywyJCFQ — counting + shelf state, no burned-in subtitles, captions via YouTube. | — | None. Keep v4 link live. |
| Evaluation evidence, including failure cases | PARTIAL | `results/holoselecta_eval_results.json` + `.csv`, `results/holoselecta_tiled_eval_results.json` + `.csv`, `results/holoselecta_failures.md`, `results/holoselecta_annotated/` (20 images), `results/real_shelf_eval_results.json` + `.csv` (5 countable real shelf stills: MAE 18.4, bias −16.4, exact 0/5, hand 175 / pred 93; 6th qualitative only), `results/real_shelf_failures.md`, `docs/EVALUATION.md`, synthetic baseline-drift test in `docs/TECHNICAL_REPORT.md` | Olly (photos) / Muse (eval + report update) | Supply staged before/after shelf photos (full baseline, then remove-2, then restock-confirm) for real drift testing. Real-shelf counting on single stills exists; real drift pairs do not — do not claim drift accuracy. |
| Core rule: OpenCV 5 for substantive analysis + a meaningful component on AWS | DONE (EC2 full app, with caveats) | OpenCV 5.0.0 verified on EC2 (/health, model_loaded true) and locally; full app (letterbox → `blobFromImage` → YOLO26n ONNX DNN `[1,300,6]` → tracker → baseline drift, primary signal) runs on EC2, not only on Lambda. Caveats: EC2 ports 8000/22 open to all for demo only; free-tier cover unconfirmed; no shop pilot. | Muse | Keep EC2 live through judging, then stop/terminate. Do not claim COOL/Agentic, counting accuracy, or a pilot. |
| COOL / Agentic Vision special awards | DONE (correctly not claimed) | `README.md` + `docs/TECHNICAL_REPORT.md` state no COOL/Agentic work | — | None. Do not claim these unless that work is actually done. |
| Devpost entry + eligibility | DONE (SUBMITTED 5/5, submission 1266470) | Devpost project https://devpost.com/software/shelfscan-tm39q7, joined and submitted 26 Oct 2026 | — | Keep SUBMITTED through judging. Organiser: competition@opencv.org. |

## Honest numbers to use (do not round these into a better story)

- HoloSelecta, first 20 images, same ground truth, conf 0.35, local, OpenCV 5.0.0:
  - Single-tile: MAE 38.05, pred 46 / GT 807, exact 0/20, within ±1 0/20.
  - Tiled 3×3 (adaptive default for high-res): MAE 26.35, pred 310 / GT 807, exact 0/20, within ±1 0/20, bias −24.85, mean latency ~1.27 s.
  - Tiling improves MAE ~31% (38.05 → 26.35) but does NOT fix counting: COCO cannot name crisps/chocolate/cans, and “refrigerator” still fires for the whole machine. Counting is NOT the primary shelf signal.
- Synthetic baseline-drift test (one vending image, painted-band test — NOT a real before/after shelf pair):
  - Same image as baseline: Full, changed_ratio 0.0.
  - Synthetic Gap: Low, changed_ratio 0.250, brightness shift 21.2.
  - Brightness +80: Check shelf, changed_ratio 0.958, shift 71.3 (guard, not a false Gap).
- Local smoke test (26 Oct snapshot): `/health` OK (OpenCV 5.0.0, yolo26n.onnx); `/api/demo` 163.8 ms; unit tests at that snapshot: 4 passed. Current suite: 39 passed locally. These are LOCAL numbers, not AWS numbers.

## Do NOT claim in the submission

- That the Lambda /health proves OpenCV loaded (it is a liveness check only; Lambda is demo-only, OpenCV NOT loaded there — the live OpenCV app is on EC2).
- Real-shelf counting accuracy, labelling accuracy, or a tested live webcam demo (no staged shelf photos supplied yet).
- App Runner as $0 (see ~$10–$15 judging-window estimate above).
- COOL or Agentic Vision.
- Eligibility as confirmed (only the organiser can confirm it).

## Submission status (current)

1. Joined Devpost and submitted (submission 1266470, 5/5, video v4, ZIP v4) before 27 Oct 2026 06:45 GMT.
2. Keep EC2 full app and Lambda demo link live for judging (27 Oct–10 Nov 2026), then stop/terminate EC2 and restrict ports.
3. No further claims without new evidence: no shop pilot, no physical pair, no time-saved figure.
