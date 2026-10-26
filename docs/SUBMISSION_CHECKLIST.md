# ShelfScan — Submission checklist

- Repo: https://github.com/OlsOls4/opencv-hackathon-2026
- Deadline: 27 Oct 2026 06:45 GMT
- Status as of 26 Oct 2026 (evening, UPDATED): SUBMITTED to Devpost
  (submission 1266470, https://devpost.com/software/shelfscan-tm39q7,
  5/5 steps, video v2 live, submission ZIP live). The submission
  remains editable until the 27 Oct 2026 06:45 GMT deadline — use
  docs/DEVPOST_DESCRIPTION.md for the improved description, and
  swap ONLY the video line when v3 is ready. Do NOT claim v3 yet.
- Judge review, 26 Oct 2026: 5 independent judges — Technical 4.8, Innovation/Impact 4.4, UX/Docs 4.7, Cloud/Reproducibility 5.0, Adversarial 4.0; average 4.58/10. Round 2: 4.78/10. Since then: full app live on EC2 (Docker build passed), 24-video guard validation (false Gaps 50 → 5), detection-improvement verdict (counting NOT headline, shelf-state only), 22 tests passed. Still to improve before deadline: v3 video, updated submission ZIP with EC2/drift/large-video results, thumbnail and image gallery in Devpost.
- This file is local-only, ready for a bulk `push_files` (excluding `.github/workflows/test.yml` and `models/yolo26n.onnx`). Do NOT push it via single-file `create_or_update_file`.
- COOL and Agentic Vision are optional and are NOT claimed.

## Requirement table

| Requirement | Status | Evidence | Owner | Exact remaining human step for Olly |
|---|---|---|---|---|
| Technical report: problem, users, architecture, OpenCV 5 implementation, AWS deployment, evaluation, limitations, responsible use | PARTIAL | `docs/TECHNICAL_REPORT.md` — covers all sections; AWS is a demo-only Lambda endpoint (not the full app), and evaluation has no real shelf data | Muse / Olly | After shelf photos exist, update the evaluation section with real results. Do not submit claiming a deployed full-app AWS outcome. |
| Judge-accessible code repo, pinned dependencies, clear build / deployment / test instructions | PARTIAL | Repo pushed 39/40 files 26 Oct 2026 (plus later bulk pushes — verify current count before submitting); `requirements.txt` pins `opencv-python-headless==5.0.0.93` and all other deps; `README.md` gives venv, install, model-download, smoke-test, uvicorn and Docker commands; `models/download_model.py` fetches ONNX (SHA256-verified) instead of committing it; `tests/` + `scripts/smoke_test.py` | Muse (file ready) / Olly (repo permissions) | For full CI only: manually add `.github/workflows/test.yml` in GitHub, or grant workflows permission — the API blocks workflow files without it. Docker-test the `Dockerfile` on the deploy machine (Docker was unavailable in this VM, so it is NOT build-tested). Open: Dockerfile untested; CI workflow not on GitHub; `results/latency.md` not yet written; Lambda demo code not in repo. None of these is claimed as done. |
| Architecture diagram showing OpenCV 5 and AWS components | PARTIAL (diagram text is stale: it still says Lambda-only + local app, not EC2) | `docs/architecture.svg` + `docs/architecture.md` — text must be updated to EC2 full app first, Lambda demo-only second, before it is relied on as the deployed architecture | Muse | Update architecture.md/svg to EC2-first before final judging. Do not submit the old Lambda-only text as the deployed architecture. |
| Working web endpoint OR arranged live screen-share | DONE (full app, EC2) | Full app live on EC2: http://16.171.250.54:8000 — /health OpenCV 5.0.0, /api/demo Low 0.216, verified from outside AWS 26 Oct 2026. Lambda demo-only link kept as secondary only. | Muse | Keep EC2 running through judging (27 Oct–10 Nov 2026), then stop/terminate and restrict ports 8000/22. Free-tier cover through judging is not confirmed from billing. |
| ≤5-minute public/unlisted video: team, app working, architecture, principal results | PARTIAL (v2 live, v3 pending) | v2 live, unlisted, 4:18: https://www.youtube.com/watch?v=ZgErR5RjIJE — real data, but engineering-heavy and shows wrong COCO boxes. v3 (shelf-state only, planned per devpost-demo-video skill, 2:30–2:45 target) is paused until detection validation, which has now landed — v3 must NOT claim counting. | Muse (v3) / parent (upload + swap link) | Upload v3, swap ONLY the video link in Devpost, keep the project SUBMITTED. Do not claim v3 until its link exists. |
| Evaluation evidence, including failure cases | PARTIAL | `results/holoselecta_eval_results.json` + `.csv`, `results/holoselecta_tiled_eval_results.json` + `.csv`, `results/holoselecta_failures.md`, `results/holoselecta_annotated/` (20 images), `results/real_shelf_eval_results.json` + `.csv` (5 countable real shelf stills: MAE 18.4, bias −16.4, exact 0/5, hand 175 / pred 93; 6th qualitative only), `results/real_shelf_failures.md`, `docs/EVALUATION.md`, synthetic baseline-drift test in `docs/TECHNICAL_REPORT.md` | Olly (photos) / Muse (eval + report update) | Supply staged before/after shelf photos (full baseline, then remove-2, then restock-confirm) for real drift testing. Real-shelf counting on single stills exists; real drift pairs do not — do not claim drift accuracy. |
| Core rule: OpenCV 5 for substantive analysis + a meaningful component on AWS | DONE (EC2 full app, with caveats) | OpenCV 5.0.0 verified on EC2 (/health, model_loaded true) and locally; full app (letterbox → `blobFromImage` → YOLO26n ONNX DNN `[1,300,6]` → tracker → baseline drift, primary signal) runs on EC2, not only on Lambda. Caveats: EC2 ports 8000/22 open to all for demo only; free-tier cover unconfirmed; no shop pilot. | Muse | Keep EC2 live through judging, then stop/terminate. Do not claim COOL/Agentic, counting accuracy, or a pilot. |
| COOL / Agentic Vision special awards | DONE (correctly not claimed) | `README.md` + `docs/TECHNICAL_REPORT.md` state no COOL/Agentic work | — | None. Do not claim these unless that work is actually done. |
| Devpost entry + eligibility | BLOCKED (not attempted) | Devpost check 26 Oct 2026: Join still shown, no late-entry ban found — but Join success is UNTESTED and Muse has not joined | Olly | Join Devpost FIRST, then submit before 27 Oct 2026 06:45 GMT. If Olly wants eligibility confirmed definitively, email the organiser at competition@opencv.org before submitting — that address, not this checklist, is the definitive check. |

## Honest numbers to use (do not round these into a better story)

- HoloSelecta, first 20 images, same ground truth, conf 0.35, local, OpenCV 5.0.0:
  - Single-tile: MAE 38.05, pred 46 / GT 807, exact 0/20, within ±1 0/20.
  - Tiled 3×3 (adaptive default for high-res): MAE 26.35, pred 310 / GT 807, exact 0/20, within ±1 0/20, bias −24.85, mean latency ~1.27 s.
  - Tiling improves MAE ~31% (38.05 → 26.35) but does NOT fix counting: COCO cannot name crisps/chocolate/cans, and “refrigerator” still fires for the whole machine. Counting is NOT the primary shelf signal.
- Synthetic baseline-drift test (one vending image, painted-band test — NOT a real before/after shelf pair):
  - Same image as baseline: Full, changed_ratio 0.0.
  - Synthetic Gap: Low, changed_ratio 0.250, brightness shift 21.2.
  - Brightness +80: Check shelf, changed_ratio 0.958, shift 71.3 (guard, not a false Gap).
- Local smoke test: `/health` OK (OpenCV 5.0.0, yolo26n.onnx); `/api/demo` 163.8 ms; unit tests 4 passed. These are LOCAL numbers, not AWS numbers.

## Do NOT claim in the submission

- A live full-app AWS/GCP endpoint, or live OpenCV inference on AWS (only a demo-only Lambda /health + /api/demo link exists, with OpenCV NOT loaded).
- That /health proves OpenCV loaded (it is a liveness check only).
- Real-shelf counting accuracy, labelling accuracy, or a tested live webcam demo (no staged shelf photos supplied yet).
- App Runner as $0 (see ~$10–$15 judging-window estimate above).
- COOL or Agentic Vision.
- Eligibility as confirmed (only the organiser can confirm it).

## Olly's submission order

1. Join Devpost (and optionally email competition@opencv.org for eligibility confirmation).
2. Keep the Lambda demo link live for judging, and either deploy the full app on AWS or arrange the screen-share fallback for the full OpenCV app, labelled honestly.
3. Supply staged shelf photos with hand counts → Muse runs the eval and updates the report.
4. Record and upload the ≤5-minute video per `docs/VIDEO_SCRIPT.md`.
5. Bulk-push this checklist + any report/eval updates (excluding `.github/workflows/test.yml` and `models/yolo26n.onnx`).
6. Paste repo + endpoint + video links into Devpost and submit before 27 Oct 2026 06:45 GMT.
