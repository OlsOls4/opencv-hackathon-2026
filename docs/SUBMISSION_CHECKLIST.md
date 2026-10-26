# ShelfScan — Submission checklist

- Repo: https://github.com/OlsOls4/opencv-hackathon-2026
- Deadline: 27 Oct 2026 06:45 GMT
- Status as of 26 Oct 2026 (evening): judge review applied (5 judges, average 4.58/10 — see below). NOT submitted to Devpost by this checklist author; a separate Devpost team may be joining/submitting in parallel, so check Devpost before claiming submission status.
- Judge review, 26 Oct 2026: 5 independent judges — Technical 4.8, Innovation/Impact 4.4, UX/Docs 4.7, Cloud/Reproducibility 5.0, Adversarial 4.0; average 4.58/10. Consensus fixes applied locally: deployment story corrected to Lambda demo-only everywhere, drift/counting limits stated plainly, shelf-state legend and restock flow added to the dashboard, /health now reports live cv2 version, video temp-file cleanup, unused PAR_LEVEL removed, Dockerfile model-download step added. Still blocking a top submission: video, real shelf data, full live OpenCV endpoint on AWS.
- This file is local-only, ready for a bulk `push_files` (excluding `.github/workflows/test.yml` and `models/yolo26n.onnx`). Do NOT push it via single-file `create_or_update_file`.
- COOL and Agentic Vision are optional and are NOT claimed.

## Requirement table

| Requirement | Status | Evidence | Owner | Exact remaining human step for Olly |
|---|---|---|---|---|
| Technical report: problem, users, architecture, OpenCV 5 implementation, AWS deployment, evaluation, limitations, responsible use | PARTIAL | `docs/TECHNICAL_REPORT.md` — covers all sections; AWS is a demo-only Lambda endpoint (not the full app), and evaluation has no real shelf data | Muse / Olly | After shelf photos exist, update the evaluation section with real results. Do not submit claiming a deployed full-app AWS outcome. |
| Judge-accessible code repo, pinned dependencies, clear build / deployment / test instructions | PARTIAL | Repo pushed 39/40 files 26 Oct 2026 (plus later bulk pushes — verify current count before submitting); `requirements.txt` pins `opencv-python-headless==5.0.0.93` and all other deps; `README.md` gives venv, install, model-download, smoke-test, uvicorn and Docker commands; `models/download_model.py` fetches ONNX (SHA256-verified) instead of committing it; `tests/` + `scripts/smoke_test.py` | Muse (file ready) / Olly (repo permissions) | For full CI only: manually add `.github/workflows/test.yml` in GitHub, or grant workflows permission — the API blocks workflow files without it. Docker-test the `Dockerfile` on the deploy machine (Docker was unavailable in this VM, so it is NOT build-tested). Open: Dockerfile untested; CI workflow not on GitHub; `results/latency.md` not yet written; Lambda demo code not in repo. None of these is claimed as done. |
| Architecture diagram showing OpenCV 5 and AWS components | PARTIAL (diagram updated, still not a deployed full app) | `docs/architecture.svg` + `docs/architecture.md` — now labelled Lambda demo-only eu-north-1 (no OpenCV) + local FastAPI + OpenCV 5 app; App Runner eu-west-2 plan is superseded | Muse | Do not submit the diagram as a deployed full-app architecture. The diagram shows the Lambda demo link plus the local OpenCV app, not a deployed OpenCV service. |
| Working web endpoint OR arranged live screen-share | PARTIAL | Lambda demo-only endpoint live (eu-north-1, /health + /api/demo only, OpenCV NOT loaded): https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/ — full stateful app NOT deployed on AWS. Do not claim live webcam, tracking, or session on AWS. | Muse / Olly | For a full-app judge path, either deploy the full app on AWS (not done) or arrange a live screen-share and say so honestly in the submission. The Lambda demo link alone is not a full-app endpoint. |
| ≤5-minute public/unlisted video: team, app working, architecture, principal results | BLOCKED (script DONE, video NOT done) | `docs/VIDEO_SCRIPT.md` — ready to record, target 3:30–4:30, shot list + recording checklist. No video file recorded or uploaded; no video link exists. | Olly only | Record per `docs/VIDEO_SCRIPT.md`, fill the numbers cards from `results/` (see below) before recording, export ≤5 minutes, upload as public or unlisted, paste the link into the Devpost submission. Muse cannot appear on camera or upload to Olly's YouTube/Vimeo/Devpost. If no endpoint exists at recording time, say on camera: “Local demo only at recording time — endpoint to follow.” Do not fake a live URL. |
| Evaluation evidence, including failure cases | PARTIAL | `results/holoselecta_eval_results.json` + `.csv`, `results/holoselecta_tiled_eval_results.json` + `.csv`, `results/holoselecta_failures.md`, `results/holoselecta_annotated/` (20 images), `results/real_shelf_eval_results.json` + `.csv` (5 countable real shelf stills: MAE 18.4, bias −16.4, exact 0/5, hand 175 / pred 93; 6th qualitative only), `results/real_shelf_failures.md`, `docs/EVALUATION.md`, synthetic baseline-drift test in `docs/TECHNICAL_REPORT.md` | Olly (photos) / Muse (eval + report update) | Supply staged before/after shelf photos (full baseline, then remove-2, then restock-confirm) for real drift testing. Real-shelf counting on single stills exists; real drift pairs do not — do not claim drift accuracy. |
| Core rule: OpenCV 5 for substantive analysis + a meaningful component on AWS | PARTIAL | OpenCV leg DONE locally: `cv2.__version__ == 5.0.0` verified, letterbox → `blobFromImage` → YOLO26n ONNX DNN `[1,300,6]` → tracker → baseline drift (primary signal, counting secondary). AWS leg PARTIAL: demo-only Lambda endpoint live, but it runs no OpenCV, no inference, no tracking — it does not by itself prove a meaningful OpenCV component on AWS. | Olly (AWS deploy) | Deploy the full OpenCV app on AWS, or state the screen-share fallback honestly, before claiming this rule is fully met. OpenCV 5 locally plus a demo-only Lambda stub does not satisfy it on its own. |
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
