# AWS free-tier component pack — ShelfScan

> Status, 26 Oct 2026: **prepared locally only, NOT deployed, NOT tested on AWS.**
> No AWS account is connected to Muse. Nothing here has been charged, created,
> or deployed. The Lambda design below is a plan, not working Lambda code.
> Do not describe it in a submission as a live, tested endpoint until the
> "before you claim it" checks in §1.5 and §4 have actually been done.

This pack exists for one reason: the OpenCV competition requires "a meaningful
component on AWS", and the original App Runner plan is **not** $0 (see §3).
The closest-to-$0 AWS component is a **Lambda demo-only** endpoint. It is
deliberately narrow: two stateless endpoints, no camera, no session
persistence. Anything that needs a continuing session still needs the
stateful App Runner service (§3) or a session store that has been built and
tested (§2) — neither of which exists yet.

Related docs: `docs/DEPLOYMENT.md` (App Runner plan, prepared only),
`docs/ZERO_COST_AWS.md` (earlier zero-cost analysis, 26 Oct 2026).
This pack supersedes neither; it is the Lambda-specific companion to them.

## Sources checked 26 Oct 2026

- AWS Lambda pricing page (`aws.amazon.com/lambda/pricing/`): free tier of
  **1,000,000 requests + 400,000 GB-seconds per month**; beyond free tier,
  $0.20 per million requests and $0.0000166667 per GB-second (x86).
  Re-verified 26 Oct 2026 from the official page text, not from memory.
- AWS App Runner pricing page (`aws.amazon.com/apprunner/pricing/`):
  **$0.064 / vCPU-hour (active) and $0.007 / GB-hour (provisioned memory)**,
  US East / EU Ireland rates. Same rates as previously verified.
- AWS Lambda docs on Function URLs: a Function URL follows standard Lambda
  pricing — **no additional charge for the URL endpoint itself**; you pay
  for invocations and compute. API Gateway, by contrast, is a separate
  service with its own charges and its own free-tier eligibility.
- DynamoDB / S3 free-tier figures in §2 are **not** re-verified from an
  official AWS page in this workstream; they are repeated from secondary
  sources found 26 Oct 2026 and are flagged "check in console" wherever
  they matter. Do not quote them in a submission as verified AWS figures
  until Olly confirms them in his own account's Billing / Free Tier usage
  view.

## 1. Minimal Lambda free-tier design — stateless endpoints only

### 1.1 What is in scope (and what is not)

| Endpoint | In the Lambda v1? | Why |
| --- | --- | --- |
| `GET /health` | Yes | Returns `{"status": "ok", "opencv": "5.0.0", "model": "yolo26n.onnx"}` without loading the model. It proves the function responds. Note honestly: the `opencv` value is currently a hard-coded string in `app/main.py`, not a live `cv2.__version__` check, so `/health` alone does **not** prove OpenCV or the model loaded. |
| `GET /api/demo` | Yes | Self-contained: it sets the full synthetic shelf as baseline, then processes the sparse synthetic shelf, all inside one invocation (`app/main.py: api_demo` → `_process`). It needs no camera, no prior baseline call, and no state carried over from an earlier request. That is exactly what makes it Lambda-safe. |
| `POST /api/frame`, `POST /api/upload`, `POST /api/baseline`, `POST /api/snapshot`, `GET /api/session`, `POST /api/session/reset`, `GET /api/export.csv`, `GET /` (dashboard page) | No — out of scope for this pack | All of them either depend on state set by an earlier call (baseline, tracker, history) or are the session/dashboard itself. See §2. Adding them later is a separate, tested piece of work, not a config change. |

Label the Lambda endpoint, wherever it is published, as:

> **Demo-only Lambda endpoint: stateless demo (`/health`, `/api/demo`) only.
> It does not carry a live session, tracker, or baseline between calls.**

Do not submit the Lambda URL as "the live ShelfScan service" without that
label. The stateful service is the App Runner plan (§3).

### 1.2 How the FastAPI app would be adapted (NOT built yet)

The current app is a long-running FastAPI server (`uvicorn app.main:app`,
see `apprunner.yaml`). Lambda does not run a long-running server; each
invocation runs a handler and then may freeze or discard the execution
environment. Two adaptation routes exist. Neither is written in this pack,
and neither has been tested — pick one, implement it, then measure (§1.5).

**Option A — Lambda container image + Web Adapter (keeps FastAPI whole).**

- Start from the existing container (Python, OpenCV 5 headless,
  YOLO26n ONNX) but change the entrypoint: instead of
  `uvicorn app.main:app --host 0.0.0.0 --port 8000`, run the app behind
  the Lambda Web Adapter (or equivalent Lambda runtime interface client)
  so HTTP requests arriving via the Function URL are translated into
  FastAPI calls.
- Advantage: `app/main.py` routes are reused unchanged, including
  `/health` and `/api/demo`.
- Disadvantage: the whole FastAPI app — including the static-file mount,
  the global `tracker`, and the global `history` list — is loaded into
  every execution environment. That state is still per-environment and
  still not shared (§2); the adapter does not fix statefulness, it only
  fixes HTTP plumbing. The image must also fit Lambda container limits
  (up to 10 GB; the existing image size has not been measured against
  that limit in this workstream).

**Option B — Small Lambda handler reusing `app/inference.py` (leaner).**

- Write a new, small handler (not yet written) that imports `Detector`
  from `app/inference.py` directly, plus the synthetic-demo image logic,
  and returns the same JSON shape as `/api/demo`.
- The demo-image helper `make_demo_image` currently lives in
  `app/main.py`, so a handler should either import it carefully or the
  helper should be moved to a shared module — importing the whole
  `app/main.py` just to reach it would drag in the FastAPI app, the
  global tracker, and the static mount, defeating the point of a lean
  handler. That refactor is part of the work, not an assumption.
- Advantage: no Web Adapter dependency, smaller surface, no FastAPI
  server process inside the function.
- Disadvantage: the handler duplicates (or must be kept in sync with)
  the `/api/demo` response shape, and any future change to demo logic
  has to be made in two places unless the shared code is properly
  factored out.

Either way, the model file (`models/yolo26n.onnx`) must be inside the
container image at build time, as it is for App Runner — Lambda has no
persistent filesystem to download it into at request time, and `/tmp`
is per-environment and ephemeral.

### 1.3 Sizing and limits — what is known, what must be measured

Known Lambda limits (from AWS docs, re-checked in general terms
26 Oct 2026):

- Memory: 128 MB to 10,240 MB, in 1 MB increments. Memory also sets
  proportional CPU.
- Timeout: up to 15 minutes per invocation; the **default is 3 seconds**,
  so a timeout must be set deliberately — do not leave it at the default
  for an OpenCV workload.
- Synchronous payload: 6 MB for request/response. `GET /api/demo`
  returns an annotated JPEG as base64 inside JSON, so its response size
  must be checked against this 6 MB limit during testing (§1.5). No
  demo-response size has been measured in this workstream, so no claim
  is made here that it fits.
- Concurrency: 1,000 concurrent executions per region by default
  (new accounts may start lower). Judge traffic is sporadic, so this is
  not expected to bind — but it is not a tested claim either.

**Not known — do not invent:**

- **Cold start for the OpenCV import on Lambda: unmeasured.** No
  Lambda cold-start latency exists anywhere in this repo. Do not carry
  any local import/inference timing over as a Lambda figure, and do not
  quote a Lambda latency in a submission until a cold invocation and a
  warm invocation have both been timed on the real function and the
  CloudWatch `REPORT` lines (billed duration, memory used) recorded.
- **Memory size that fits OpenCV 5 + YOLO26n comfortably: unmeasured
  on Lambda.** Start testing from the CloudWatch `REPORT` line's
  "Max Memory Used" and size from that evidence, not from a guess.
  Provisioned concurrency — which would mask cold starts — is a paid
  feature and is **not** part of this free-tier design; do not enable it
  and still call the result free.

### 1.4 Free-tier arithmetic (formula shown; judge numbers are illustrative)

Verified free tier (official Lambda pricing page, 26 Oct 2026):

- 1,000,000 requests per month.
- 400,000 GB-seconds of compute per month.
- Beyond free tier: $0.20 per million requests, $0.0000166667 per
  GB-second (x86).

Headroom formula (per calendar month, per account — not per function):

```
GB-seconds used = requests × memory_in_GB × duration_in_seconds
request headroom % = requests / 1,000,000 × 100
compute headroom % = GB-seconds used / 400,000 × 100
```

Illustrative example only — **not** a measurement of ShelfScan on Lambda:

```
1,000 requests × 1 GB × 1 second = 1,000 GB-seconds
= 0.1% of the request allowance, 0.25% of the compute allowance
```

At 1 GB, the full 400,000 GB-second allowance is 400,000 seconds of
execution; at 2 GB it is 200,000 seconds. Judge traffic in the hundreds
to low thousands of demo calls is therefore *expected* to sit far inside
both caps — but the actual GB-seconds depend on the real memory and
duration, which are unmeasured (§1.3), so the only honest statement
before testing is: "inside the free tier **if** measured usage stays
below these caps, **and if** no other workload in the same account has
already consumed that month's allowance."

Caveats that break a naive "$0" claim:

- The allowance is **per account, per calendar month**, shared across
  every Lambda function in the account. The judging window
  (27 Oct–10 Nov) straddles a month boundary, so it draws on part of
  October's allowance and part of November's — check both months in
  Billing, do not treat the window as a single month's bucket.
- Anything else in Olly's account that uses Lambda that month eats the
  same allowance.
- The Lambda free tier does **not** cover the services around Lambda
  (see §1.5/§2): CloudWatch Logs ingestion, data transfer out beyond
  the free allowance, ECR storage, or any DynamoDB/S3 usage beyond
  their own free tiers. Keep logs minimal during judging (no per-frame
  debug dumps) and check Billing, not just the Lambda line.

### 1.5 Function URL vs API Gateway — cost note

- **Prefer a Lambda Function URL for the judge demo endpoint.**
  Per AWS Lambda docs, a Function URL follows standard Lambda pricing:
  **no additional charge for the URL endpoint itself** — only the
  invocation and compute charges (§1.4), plus any data transfer out
  beyond the free allowance. It is an HTTPS endpoint, which fits a
  submission link, and it needs no extra service to configure.
- **API Gateway is not needed for two endpoints and is not free by
  default.** It is a separate service with its own per-request charges
  and its own free-tier eligibility, which depends on the account type
  and age (older 12-month free-tier accounts vs newer Free Plan /
  credit-based accounts differ — see the §2 warning about checking the
  console). Do not add API Gateway "just in case" and still call the
  pack free-tier-only. Only add it if a feature it alone provides
  (usage plans / API keys, request validation, a custom domain without
  CloudFront, WAF) is actually required — and then price that feature
  separately.
- **Function URL auth trade-off, stated plainly:** with auth type
  `NONE`, the URL is public and anyone who finds it can invoke it and
  spend the free-tier allowance. With `AWS_IAM`, callers must sign
  requests (SigV4), which judges will not do from a plain browser link.
  For a judge-facing demo link, `NONE` is the usable option — so do
  not publish the URL anywhere except the submission itself, set a
  billing alarm before publishing (§4), watch invocation counts during
  judging, and be ready to disable the Function URL if abuse appears.
  There is no free, judge-friendly, abuse-proof option here; do not
  pretend otherwise.

### 1.6 Before you claim it (acceptance checks for the Lambda build)

None of these has been done. Each must pass before the Lambda URL is
put in a submission:

1. Cold invocation and warm invocation of `/health` and `/api/demo`
   timed on the real function; `REPORT` billed duration and max memory
   recorded.
2. `/api/demo` response size checked against the 6 MB synchronous
   payload limit.
3. `/api/demo` output compared against the local `/api/demo` output
   (same synthetic shelf, same Gap state, annotated image present).
4. Two near-simultaneous `/api/demo` calls return consistent results
   (they will, because demo is self-contained — this check is the
   proof that no hidden shared state is involved).
5. Billing / Free Tier usage view checked after the test calls, showing
   usage inside the Lambda allowance and no unexpected charge from
   logs, transfer, or ECR.

## 2. Session-store note — why Lambda alone breaks the live session

### 2.1 The current app is stateful (grounded in `app/main.py`)

These are module-level globals, created once per server process:

- `tracker = Tracker(max_missed=5)` — `app/tracker.py` keeps `tracks`
  (id → box/label/missed), `next_id`, and `unique_seen`.
- `history = []` — capped to the last 200 entries in `_process`.
- `detector` (lazy singleton) — `Detector` in `app/inference.py` keeps
  `_baseline_gray` and `_baseline_roi` after `POST /api/baseline`.

The dashboard reads all of it: `GET /api/session` reports
"Visible now" (tracks with `missed == 0`) and "Unique seen"
(`tracker.unique_seen`), plus the last 50 history entries;
`GET /api/export.csv` dumps `history`; `POST /api/session/reset`
clears tracker and history.

### 2.2 What breaks on Lambda, and why "warm" does not save it

Lambda execution environments **may** be reused for a later invocation
(warm start), but reuse is never guaranteed, and concurrent invocations
run in **separate** environments with separate globals. Consequences,
stated without softening:

- **"Visible now" breaks:** track IDs are assigned per-environment.
  Two judges (or two tabs) hitting the function at once see different
  track sets; a track created in one environment is invisible in
  another.
- **"Unique seen" breaks:** `unique_seen` and `next_id` reset whenever
  a new environment starts, so the count restarts and IDs repeat.
  It is no longer a session total, it is a per-environment accident.
- **Baseline persistence breaks:** a baseline captured by
  `POST /api/baseline` in one environment is absent in the next
  environment, so a later frame falls back to "No baseline" (or to
  whatever baseline that environment happened to set). The occupancy
  state (Full / Low / Gap) then depends on which environment served
  the call, not on the shelf.
- **History and CSV export break:** `history` is per-environment, so
  `GET /api/session` and `GET /api/export.csv` return only the calls
  that happened to land on that environment — a partial, misleading
  record, not a session log.
- **Reset breaks:** `POST /api/session/reset` clears one environment's
  state and leaves every other environment untouched.

This is why §1 scopes Lambda v1 to `/health` and `/api/demo` only.
`/api/demo` survives because it sets its own baseline and processes
its own frame inside a single invocation; it never reads state written
by an earlier call.

### 2.3 Minimal store that would be needed — and its own free-tier limits

To make the live session work on Lambda, the globals in §2.1 must move
out of process memory into a store that every environment reads and
writes. The minimal shape (design only, not built) is:

- One session record per judging/demo session (session id, created
  time, expiry), holding tracker state (active tracks, `next_id`,
  `unique_seen`) and history entries.
- A baseline reference (see the baseline warning below), readable by
  any environment.
- Read-modify-write on every frame with a concurrency guard, so two
  simultaneous frames do not overwrite each other's track updates;
  plus a TTL/expiry so abandoned sessions do not accumulate, and a
  reset that deletes the stored record (not just one environment's
  copy). Export must read from the store, not from memory.

Candidate stores, with the free-tier check still owed:

- **DynamoDB (preferred candidate for tracker/history state).**
  Secondary sources found 26 Oct 2026 describe an always-free allowance
  of **25 GB storage, 25 provisioned read capacity units (RCU) and
  25 provisioned write capacity units (WCU) per region per payer
  account, plus 2.5M Streams read requests/month** — but with a trap
  that matters: **the capacity-unit allowance applies to provisioned
  mode only; an on-demand table has no free request allowance and
  pays from the first request.** A ShelfScan table must therefore be
  created in provisioned mode at or below 25 RCU / 25 WCU (shared
  across all tables in that region/account) to stay inside that
  allowance, and usage must be checked in Billing. These figures are
  **not** verified from an official AWS page in this workstream —
  confirm them in Olly's console before building on them. Judge-scale
  tracker writes (one small write per frame) are far below 25 writes/
  second in principle, but "in principle" is not a test.
- **S3 (candidate for baseline images / exported CSV objects, not for
  per-frame tracker state).** Legacy 12-month free-tier accounts are
  described in secondary sources as 5 GB Standard storage, 20,000 GET
  and 2,000 PUT requests/month. **Do not assume this applies to Olly's
  account:** accounts created on/after July 2025 fall under a
  different Free Plan / credit model (credits, shorter runway), not
  the legacy per-service allowances. Check the account's actual Free
  Tier view first. S3 is also the wrong shape for per-frame tracker
  updates (object overwrite per frame, no atomic read-modify-write
  for track IDs) — use it for blobs (a baseline image, a finished
  CSV), not as the tracker store.
- **Baseline warning:** a baseline is a blurred grayscale image crop
  (`Detector._baseline_gray`), not a small JSON value. Storing it in
  DynamoDB directly runs into the 400 KB item-size limit (verify in
  console/docs before designing around it); the cleaner design is to
  store the original baseline image in S3 and re-derive the blurred
  crop on read, or to store only compact occupancy parameters — but
  that choice changes what "baseline persistence" means and must be
  designed and tested, not assumed. Until it is, baseline persistence
  on Lambda is unsolved.

### 2.4 Labelling rule until the store is built and tested

Until the store in §2.3 is implemented **and** passes multi-environment
tests (two concurrent callers, baseline set in one call and read in a
later call served by a different environment, reset visible everywhere,
export complete), the Lambda endpoint must be labelled **demo-only**
(§1.1) in the submission and must not be described as live tracking,
a live session, or a persistent dashboard. The App Runner service (§3)
remains the only currently-planned route to a stateful live endpoint,
and it is not free.

## 3. Paused App Runner cost note

App Runner is the original plan (`docs/DEPLOYMENT.md`, `apprunner.yaml`:
2 vCPU / 4 GB, eu-west-2, health check `/health`). Its cost, with
formula shown:

```
Provisioned memory alone: 4 GB × $0.007 / GB-hour = $0.028 / hour
Judging window 27 Oct–10 Nov = 14 days = 336 hours
Provisioned memory for the window: $0.028 × 336 = $9.41
Active CPU, if busy: 2 vCPU × $0.064 = $0.128 / hour (only while active)
Realistic total for the window, sporadic judge traffic: roughly $10–$15
```

That $10–$15 is an **estimate, not a cap**: it excludes build minutes,
CloudWatch Logs, and data transfer out, which bill separately, and
actual active-CPU time depends on real judge traffic. It is also not
$0 in any reading.

**Pausing:** pausing an App Runner service stops provisioned charges
(AWS's own App Runner pricing examples show a service paused for the
hours it is not used, paying only for the hours it runs). That is a
cost-saving control, not a deployment strategy:

- A paused service is **not a live judge endpoint**. Judges hitting a
  paused URL do not get ShelfScan; they get nothing usable. Do not
  submit a paused service's URL as a live endpoint, and do not describe
  a paused service as "deployed".
- Pausing only helps between judging (or before judging starts, while
  the service is being prepared). During 27 Oct–10 Nov, the service
  must be running to be judged, so the ~$10–$15 window cost applies
  if App Runner is the live route.
- Pausing does not delete the service: remember to delete it after
  judging (§4) rather than leaving it paused indefinitely and
  assuming that is the same as gone.

**Unverified third-party claim, carried over honestly:** a third-party
listing claimed App Runner was "closed to new customers since
2026-04-30". That claim was **not** found on the official AWS pricing
page checked for this pack, so it is treated as unverified — Olly must
check in his own AWS console whether App Runner service creation is
available for his account before relying on either the claim or this
plan. If App Runner creation is unavailable, §1 (Lambda demo-only)
plus a live screen-share fallback is the remaining AWS-component
route, and that limitation must be stated in the submission rather
than hidden.

## 4. Exact steps Olly would take in his own AWS account

No AWS account is connected to Muse, and Muse must not create one,
use credentials, or deploy. These steps are for Olly, in his own
account, in his own browser/console. Region: **eu-west-2 (London)**,
to match the existing App Runner plan, unless the console shows a
reason to differ; keep any future DynamoDB table in the same region
as the function.

### 4.1 Before anything is created (do this first)

1. Sign in to Olly's own AWS account (do not share credentials with
   Muse or paste them anywhere in this repo).
2. Open Billing → Budgets and create a billing alarm/budget with a
   low early-warning threshold (for a free-tier-only attempt, a $1
   alarm is a sensible tripwire; the App Runner plan separately used
   a $10–$20 alarm — do not confuse the two). Confirm the alarm
   notifies an email Olly actually reads.
3. Open Billing → Free Tier usage and note, for the current month:
   how much Lambda request / GB-second allowance is already used,
   whether DynamoDB provisioned capacity allowance is available, and
   which free-tier model the account is on (legacy 12-month vs newer
   Free Plan / credits). Screenshot or note the numbers — they decide
   whether "inside free tier" is true for this account.
4. Confirm App Runner service creation is available in the console
   (§3 unverified claim check). This decides whether the stateful
   route is even an option.

### 4.2 Build the Lambda demo function (code work first, console second)

5. Implement one adaptation route from §1.2 (container + Web Adapter,
   or small handler reusing `app/inference.py`). This code does not
   exist yet — it is not a console-only task.
6. Build the container image locally and test it locally first
   (container invocation of `/health` and `/api/demo`, response size
   noted). Only then push the image to Amazon ECR in Olly's account
   (create one ECR repository for ShelfScan; note its URI).
7. In Lambda → Create function → Container image: select the ECR
   image; set a deliberate timeout (not the 3-second default) and an
   initial memory setting to be tuned from CloudWatch `REPORT` data;
   do **not** enable provisioned concurrency.
8. In the function configuration, enable a Function URL with auth
   type `NONE` for the judge demo link (see the abuse warning in
   §1.5). Record the Function URL — this is the only URL to submit
   for the Lambda component, labelled demo-only (§1.1).
9. Test from an incognito window / second device (not just the same
   browser session): `GET <Function URL>/health`, then
   `GET <Function URL>/api/demo`. Confirm the demo returns the Gap
   state and an annotated image, and that the response is under the
   6 MB synchronous limit.
10. Read the CloudWatch Logs `REPORT` lines for the cold and warm
    calls (billed duration, max memory used). Record the real numbers
    in the submission notes; replace every "expected to be inside
    free tier" in this pack with the measured numbers.
11. Re-check Billing → Free Tier usage after the test calls. If any
    unexpected charge appears (logs, transfer, ECR), stop and fix it
    before submitting the URL.

### 4.3 If the stateful route is also wanted

12. **Either** follow `docs/DEPLOYMENT.md` for App Runner (2 vCPU /
    4 GB, eu-west-2, health check `/health`, billing alarm $10–$20,
    pin/disable auto-deploy after submission, keep live 27 Oct–
    10 Nov), accepting the ~$10–$15 window estimate in §3;
    **or** build and test the §2.3 session store first and re-run the
    §1.6 acceptance checks plus multi-environment session tests.
    Do not do "Lambda + hope" as a substitute for either.

### 4.4 Delete after judging (do not skip)

After 10 Nov (or as soon as judging no longer needs the endpoint):

1. Delete the Lambda function (this also removes its Function URL).
2. Delete the ECR repository / image (deleting the function alone
   does not delete the stored image).
3. Delete any DynamoDB table and any S3 bucket/objects created for
   this pack (empty buckets before deleting them; check for
   versioned objects if versioning was ever enabled).
4. Delete the App Runner service if one was created (pausing is not
   deleting — §3).
5. Check CloudWatch Logs and delete the function's log group if it
   remains after function deletion; check log retention settings on
   anything left behind.
6. Open Billing and confirm no App Runner, Lambda, ECR, DynamoDB, S3,
   or CloudWatch resources remain, and that the final bill for the
   judging period matches expectations. Keep that final Billing
   screenshot/note with the submission records.

## 5. What is NOT done (blockers / open items)

- No AWS account connected to Muse; no credentials used, shared, or
  requested by this pack.
- No Lambda handler, Web Adapter configuration, or Dockerfile change
  written; §1.2 is a design, not code.
- No Lambda cold-start latency measured; no memory sizing measured;
  no `/api/demo` response size measured against the 6 MB limit.
- No session store built or tested; Lambda is demo-only until §2.3
  exists and passes multi-environment tests.
- DynamoDB and S3 free-tier figures in §2.3 not verified from an
  official AWS page in this workstream — confirm in Olly's console.
- App Runner availability for new customers unverified (§3) — check
  in Olly's console.
- No deployment, no charge, no GitHub push made by this workstream.
  This file is local only, ready for a bulk `push_files` push
  (excluding `.github/workflows/test.yml` and `models/yolo26n.onnx`)
  if a push is wanted.
