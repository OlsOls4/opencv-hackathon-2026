# Supermarket Empty Shelf Detector — evaluation BLOCKED (no download, no metrics)

**Status: BLOCKED. No images were downloaded, no evaluation was run, and no
numbers exist for this dataset. Do not claim a Gap / Low result, a counting
result, or a labelling result from this dataset.**

## Target dataset (as identified on the Roboflow page)

- Roboflow Universe — Supermarket Empty Shelf Detector, by FYP
  (`fyp-ormnr/supermarket-empty-shelf-detector`)
- 497 images, single class OOS (out-of-stock), CC BY 4.0 on the Roboflow page
- Project page (checked 2026-10-26): https://universe.roboflow.com/fyp-ormnr/supermarket-empty-shelf-detector
- Intended evaluation (not run): first 20 images only, Gap / Low state only,
  using ShelfScan baseline/occupancy logic and/or OOS box presence as a Gap
  indicator. It would never have been counting accuracy or labelling accuracy:
  the dataset has a single OOS class and no product counts.

## What blocked it

A free Roboflow account + API key is required to download this dataset.
No unauthenticated direct download link was found, and no account was
created, no credential was used, and nothing was paid — per the task's
stop condition, that route was stopped, not worked around.

Evidence checked 2026-10-26:

1. **Project page text fetch** — the fetched page exposes no ZIP/download
   link for the dataset. Its only code snippet is an inference call that
   requires an API key:
   `InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key=...)`
   with `model_id="supermarket-empty-shelf-detector/4"`.
2. **Roboflow SDK / CLI docs** — every download route takes an API key:
   `Roboflow(api_key="...")` then `project.version(...).download(...)`, and
   `roboflow download -f <format> <workspace/project/version>`. The docs'
   own note for public Universe projects is only that you need not be a
   member of the owning workspace — "your API key just needs Universe
   access". An API key is still required.
3. **Supervision / Roboflow tutorial docs** — "log into your Roboflow
   account and download the dataset", with `roboflow.login()` in the
   example code.
4. **Roboflow Universe download docs** — the ZIP route is a click-through
   in the Roboflow web app ("Dataset" sidebar → "Download Dataset" →
   "Download dataset" → choose format → "Download as a ZIP" / "Show
   download code"). That web-app click-through was not performed here:
   this agent cannot operate a live browser, and the code routes above
   show the download is keyed to an account in any case.
5. **No verified unauthenticated mirror found** — web searches for the
   exact project name, image count (497), and OOS class returned only the
   Roboflow page itself, a Hugging Face model repo that cites the dataset
   but hosts no dataset images (`wiwiewei18/smart-shelf-tracker`, a
   YOLO11n model only), and papers citing the Roboflow source. No Kaggle,
   GitHub, or other mirror of the 497-image export was verified, so no
   substitute images were used — substituting unverified images would
   have broken the "Roboflow supermarket shelves" domain claim.

## What was NOT done

- No Roboflow account created, no login, no API key obtained or used.
- No dataset images downloaded (0 images, local or otherwise), and no
  dataset images pushed to GitHub or committed anywhere.
- No `results/empty_shelf_eval_results.csv` written — writing one would
  have required invented numbers, which the task forbids.
- No metrics run: n = 0, no Gap/Low counts, no OOS-box counts, no latency.
  There is nothing to report as a result, and the HoloSelecta failures
  note was not reused as a substitute for this dataset.

## What would unblock it (parent decision, not done here)

- A human (or an eligible parent/root agent with live-browser access)
  creates a free Roboflow account, or supplies an API key through the
  approved secure flow, and downloads the YOLO-format export for
  `fyp-ormnr/supermarket-empty-shelf-detector` (dataset version to be
  confirmed on the Dataset page at download time — the model version 4
  on the project page is not, by itself, proof of the dataset version).
- Then, and only then, run the planned first-20 Gap-only evaluation
  locally, keep the images local (never push them to GitHub), and write
  `results/empty_shelf_eval_results.csv` plus
  `results/empty_shelf_failures.md` with n, condition, and domain stated.
  Until that happens, the parent must not claim this second-dataset
  evaluation in any submission, report, or summary.
