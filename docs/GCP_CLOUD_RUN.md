# ShelfScan on Google Cloud Run — deploy pack (prepared only, NOT deployed)

> ⚠️ **GCP DOES NOT satisfy the OpenCV competition's "meaningful component
> on AWS" requirement.**
>
> A Cloud Run endpoint is a **demo / judge-access convenience only**. The
> competition still needs a **separate, meaningful AWS component** — that is
> the AWS workstream's job, not this one. Do not describe the GCP endpoint
> in the submission as the AWS component, and do not drop the AWS work
> because this GCP pack exists. If only one endpoint can be kept live for
> judging (27 Oct–10 Nov), keep the AWS one and treat GCP as a spare.

Status: local files only. Nothing has been deployed, no GCP project or
billing account has been created, and no credentials were used. The owner
(Olly, ollymcbride4@gmail.com) must run the steps below.

## 0. What was verified, and what was not

Figures below are from the official Cloud Run pricing page fetched
26 Oct 2026: https://cloud.google.com/run/pricing — unless marked
otherwise. Re-check that page at deploy time; prices and tiers change.

### Verified from the official pricing page (request-based billing)

| Item | Figure |
| --- | --- |
| Free tier, CPU | First **180,000 vCPU-seconds / month** |
| Free tier, memory | First **360,000 GiB-seconds / month** |
| Free tier, requests | **2 million requests / month** |
| Free tier scope | Aggregated across projects **by billing account**, resets **every month**; billed only past the free tier |
| Free-tier basis | Applied as a **spending-based discount using Tier 1 pricing** (see region warning below) |
| Beyond free tier (us-central1 figures shown) | CPU **$0.000024 / vCPU-second**, memory **$0.0000025 / GiB-second**, requests **$0.40 / million**; idle min-instance time $0.0000025 / unit-second |
| Billing granularity | Rounded up to the nearest **100 ms** |
| Egress | Outbound internet transfer at networking prices, with **1 GiB free within North America / month** |
| Instance-based billing (NOT used here) | 240,000 vCPU-seconds and 450,000 GiB-seconds free / month |

### Always-free vs the 90-day trial — read this before assuming "$0 forever"

- The Cloud Run monthly allowances above are a **recurring monthly** free
  tier: the official page says the free tier "resets every month" and is
  aggregated by billing account. Multiple secondary sources describe this
  as the "Always Free" tier with no end date, **distinct** from the
  new-customer **$300 / 90-day trial credit**. That "no end date"
  wording was **not** in the official excerpt fetched for this pack, so
  treat it as corroborated-but-not-officially-verified here, and confirm
  in the console at deploy time.
- The $300 / 90-day trial is a **separate, one-off, new-customer**
  offer. Do not budget the judging window on the assumption that trial
  credit will cover overages — judge traffic should fit the monthly
  allowances above.
- A **billing account is required even for free-tier use** (the free tier
  is aggregated by billing account). Expect to add a payment method for
  verification when creating/linking the billing account. That is the
  main non-technical blocker for a truly $0 setup.

### Region warning (the main $0 risk)

- The free-tier figures are explicitly **"based on us-central1 pricing"**
  and applied as a discount at Tier 1 prices. In a region priced above
  Tier 1, the same discount covers **fewer** vCPU-/GiB-seconds.
  The exact effective allowance for europe-west1 / europe-west2 was
  **not verified from the official page in this check** — do not quote
  a London effective figure from memory or secondary sources.
- This pack defaults to **europe-west1 (Belgium)** as the near-UK
  candidate, but **verify its price tier in the console / pricing
  calculator before deploying**. If it prices above Tier 1, either
  accept the smaller effective allowance (still likely $0 for low judge
  traffic) or deploy to **us-central1 (Iowa)** instead, where the
  quoted figures apply literally, at the cost of higher UK latency.
- Second $0 risk: **egress outside North America is not covered by the
  1 GiB North America allowance** and is charged at networking prices
  (rate unverified here). Annotated images from `/api/demo` are base64
  JPEGs, so each demo response is not tiny. Judge traffic only, no
  public promotion, no uptime pinger hitting the demo endpoint — a
  keep-alive pinger would also burn free-tier seconds for no benefit.
  `/health` is cheap; still, do not ping it more than needed.

### Costs NOT covered by the Cloud Run figures above

- **Artifact Registry image storage** and **Cloud Build build minutes**
  are separate products with their own billing. Keep exactly one image
  tag, delete superseded images, and check the first bill after the
  first build. No figure is quoted here because none was verified from
  an official page in this check.
- Budgets **alert; they do not cap spending**. A budget alert is not a
  spend cap. The real $0 controls are: min-instances 0, max-instances 3,
  no always-on instance, no database, no load balancer.

## 1. Dockerfile verdict — one-line fix applied and tested locally

**Before:** `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",
"--port", "8000"]` — hardcoded port 8000. Cloud Run sets `$PORT`
(default 8080) and expects the container to listen on it, so the old
image would not receive traffic on Cloud Run.

**After (this pack, only change made):**

```dockerfile
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

No other Dockerfile change. `EXPOSE 8000` is documentary only and was
left alone; `cloudrun.yaml` declares `containerPort: 8080` to match
Cloud Run's default `$PORT`.

**Local test of the exact new CMD logic (Docker is not installed in
this environment, so the container itself was not built or run):**

- `PORT=8123` → app served on 8123; `GET /health` returned
  `{"status":"ok","opencv":"5.0.0","model":"yolo26n.onnx"}` and
  `GET /api/demo` returned a valid result (latency 146.7 ms warm).
- `PORT` unset → app served on the 8000 default; `GET /health` OK.
- Resident memory after one demo request: ~159 MiB (single worker).
  The 2 GiB limit below therefore has large headroom for larger uploads
  and video frame sampling; raise it only if you see out-of-memory
  restarts, and note that more memory burns GiB-seconds faster.

**Other Cloud Run suitability notes:**

- **Stateless enough for a demo, not truly stateless.** Tracker state
  and `history` live in process memory (`app/main.py`), capped at 200
  entries, and are per-instance. With max-instances 3, `/api/session`
  and `/api/export.csv` reflect only the instance that served the
  request, and everything resets on scale-to-zero or a new revision.
  `/api/demo` works on any instance, so judges should use that path.
  Do not present session history as durable data.
- **Cold start is real.** `cv2` is imported at app startup and the
  YOLO model is loaded lazily on the first inference request
  (`get_detector()`); `/health` does **not** load the model, so a
  passing health check does not mean the first demo will be fast.
  The 300 s request timeout below exists for that first request.
  Warm the service with one `/api/demo` call before sharing the URL.
- **No local disk dependence.** Uploads/video go to `/tmp` (ephemeral)
  and are not persisted; nothing in the app writes to a volume.
- **Image contents.** The Dockerfile copies only `app/`, `models/` and
  `scripts/`. The model file is 9.5 MB (`models/yolo26n.onnx`). Note
  for the GitHub push: if `models/yolo26n.onnx` is excluded from the
  push (as instructed for the bulk push), **deploy from this local
  checkout, not from a fresh GitHub clone** — or run
  `python models/download_model.py` first (it verifies the SHA256).
- `.gcloudignore` (new, repo root) excludes `.venv/`, `.git/`,
  `results/`, `*.mp4` etc. from the upload to Cloud Build.

## 2. Deploy steps (Olly runs these; nothing here runs itself)

Prerequisites: `gcloud` CLI installed, signed in as
ollymcbride4@gmail.com, and a billing account you are willing to link
(payment method required for verification even for free-tier use).

```bash
# 1. Sign in and create a dedicated project (project IDs are globally
#    unique — pick another suffix if shelfscan-demo is taken).
gcloud auth login
gcloud projects create shelfscan-demo --name="ShelfScan demo"
gcloud config set project shelfscan-demo

# 2. Link billing (replace BILLING_ACCOUNT_ID with yours from
#    `gcloud billing accounts list`). Without this, Cloud Run deploy fails.
gcloud billing accounts list
gcloud billing projects link shelfscan-demo --billing-account=BILLING_ACCOUNT_ID

# 3. Enable the APIs used by a source deploy.
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# 4. Deploy from this local directory (NOT from a GitHub clone without
#    the model file — see section 1). First deploy builds the image.
#    --allow-unauthenticated makes the judge URL public; without it
#    judges get a 403. No IAM / login is needed for this demo.
gcloud run deploy shelfscan \
  --source . \
  --region europe-west1 \
  --cpu 1 \
  --memory 2Gi \
  --min-instances 0 \
  --max-instances 3 \
  --concurrency 10 \
  --timeout 300 \
  --port 8080 \
  --allow-unauthenticated

# 5. Verify (replace URL with the one printed by the deploy).
curl https://<service-url>/health
curl https://<service-url>/api/demo | head -c 400
#    Then open https://<service-url>/ in a browser, incognito, and from a
#    second device if possible. Record the real URL in the submission —
#    do not paste a placeholder URL.
```

Equivalent declarative form: edit `PROJECT_ID` in `cloudrun.yaml`
(repo root), build/push the image to Artifact Registry, then
`gcloud run services replace cloudrun.yaml --region europe-west1`.
The `gcloud run deploy` command above is the recommended path because
it also sets `--allow-unauthenticated`, which the YAML alone does not.

**Region choice at deploy time:** if the console shows europe-west1
priced above Tier 1 and you want the quoted free-tier figures to apply
literally, re-run step 4 with `--region us-central1` (and change the
image path in `cloudrun.yaml` to match). Do not deploy to
europe-west2 (London) without checking its tier first — secondary
sources price London above Tier 1, which shrinks the effective free
allowance.

## 3. Keeping it at $0 during judging (27 Oct–10 Nov)

- Keep exactly this configuration: min 0, max 3, 1 vCPU, 2 GiB, no
  database, no load balancer, no VPC connector, no scheduled pinger.
- Share the URL only with judges / in the submission, not publicly.
- Check billing at least twice during the judging window:
  Cloud Console → Billing → Reports, filter by project
  `shelfscan-demo` and service Cloud Run. If any charge appears,
  check egress first (section 0), then instance count.
- Set a budget alert on day one (Console → Billing → Budgets & alerts,
  e.g. $1): remember it **alerts only** — if it fires, delete or
  restrict the service (section 4) rather than assuming it stopped.
- After submission, pin the deployed revision: do not redeploy or push
  a new image to the same service until judging ends, or judges may
  hit a different revision mid-review.

## 4. Delete it after judging (do this promptly after 10 Nov)

Deleting the whole project removes the service, images and billing
linkage in one step and is the recommended cleanup:

```bash
gcloud projects delete shelfscan-demo
# If you want to keep the project but stop all charges:
#   gcloud run services delete shelfscan --region europe-west1
#   # then delete the Artifact Registry images for shelfscan too.
```

After deletion, confirm in the console that the service is gone and
check the final billing report. Keep the AWS endpoint decision
separate: deleting GCP does not affect the AWS requirement, and
deleting GCP does not delete the AWS component.

## 5. Files in this pack

- `cloudrun.yaml` — repo root, declarative service definition
  (PROJECT_ID placeholder must be replaced before use).
- `docs/GCP_CLOUD_RUN.md` — this file.
- `.gcloudignore` — repo root, keeps the build context small.
- `Dockerfile` — one-line CMD change only (see section 1).

## 6. Blockers / not done

- NOT deployed; no GCP project, billing account or credentials exist
  in this workspace, and none were created or used.
- Docker is not installed in this environment, so the container image
  itself was **not** built or run — only the CMD's port logic was
  tested locally via uvicorn (section 1). The first real
  `gcloud run deploy` is also the first container build test; if it
  fails on memory or startup time, the documented fallbacks are
  memory 4 GiB, then timeout review — not a min-instance (which would
  break the $0 intent).
- Region tier for europe-west1, egress rates outside North America,
  Artifact Registry / Cloud Build charges, and the "no end date"
  wording for Always Free were **not** verified from an official page
  in this check — verify each in the console at deploy time and do
  not quote them as verified figures.
- The AWS "meaningful component" is out of scope for this pack (see
  the banner at the top) and remains a separate workstream.
