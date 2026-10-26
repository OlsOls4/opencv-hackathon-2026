# Zero-cost AWS option — prepared, NOT deployed

## Why the original App Runner plan is not zero cost

Official AWS App Runner pricing (checked 26 Oct 2026, US East / EU Ireland
rates shown on the AWS pricing page):
- $0.064 / vCPU-hour, charged only while an instance is actively processing
- $0.007 / GB-hour, charged continuously for provisioned memory

ShelfScan's planned size is 2 vCPU / 4 GB, 1 provisioned instance:

- Provisioned memory alone: 4 GB x $0.007 = $0.028/hour
- 24 hours: $0.67/day
- Judging window 27 Oct–10 Nov (14 days, 336 hours): $9.41 for provisioned
  memory alone, before any active CPU time, requests, logs, or data transfer
- Active CPU, if fully busy: 2 vCPU x $0.064 = $0.128/hour. Judge traffic
  is sporadic, so the realistic total for the judging window is roughly
  $10–$15, not $0, and not the $10–$20 billing alarm's upper end by much.

Pausing an App Runner service stops provisioned charges, but an endpoint
that is paused is not a live judge endpoint. Do not claim App Runner is
free, and do not leave it running past judging without deleting it.

A third-party listing claimed App Runner was "closed to new customers
since 2026-04-30". That claim was NOT found on the official AWS pricing
page checked above, so it is treated as unverified — check the AWS console
for the actual account before relying on either claim.

## Closest zero-cost AWS route: Lambda (always-free tier)

Official AWS Lambda pricing (checked 26 Oct 2026):
- Free tier, every month, for new and existing accounts: 1,000,000 requests
  + 400,000 GB-seconds
- After free tier: $0.20 per million requests, $0.0000166667 per GB-second

ShelfScan's measured local latencies (not AWS latencies):
- /api/demo: 163.8 ms
- Real-object photo (bus, 5 detections): 301 ms

At 1 GB Lambda memory and ~0.3 s per frame:
- 0.3 GB-seconds per frame
- 400,000 GB-seconds covers ~1.3 million such frames by compute alone;
  the 1,000,000-request cap binds first
- Judge traffic (hundreds to low thousands of frames) is orders of
  magnitude inside both free-tier caps, so Lambda compute itself can be $0
  for judging, IF no other service in the account has already used the
  free tier that month.

Other costs to check before claiming "$0 total":
- API Gateway / Function URL: Function URLs avoid API Gateway charges;
  prefer a Lambda Function URL for the judge endpoint if it fits the
  submission's HTTPS requirement
- CloudWatch Logs: small, but log ingestion is not unlimited — keep logs
  minimal during judging
- S3 / DynamoDB if used for session storage: each has its own free tier;
  do not assume they are free without checking that month's usage
- Data transfer out: judge traffic is small (annotated JPEGs), but it is
  not automatically free

## What Lambda changes (honest rework, NOT built yet)

The current app is a stateful FastAPI server: in-memory session, tracker
with persistent IDs, baseline, history, CSV. Lambda is stateless between
invocations:

- What works unchanged in a Lambda port: /health, /api/demo,
  POST /api/upload (single image/video, stateless), /api/frame if each
  frame is treated independently
- What breaks without rework: "Visible now" / "Unique seen" tracker IDs,
  baseline persistence, restock history, and CSV export across frames,
  because a warm Lambda instance is not guaranteed to serve the next frame
- Minimum rework for a credible Lambda version: external session store
  (DynamoDB free tier or S3) for baseline + tracker state, or a clearly
  labelled stateless demo mode only — do NOT claim live tracking works
  on Lambda until that store is built and tested
- Container image: same Dockerfile base (Python 3.12-slim, OpenCV 5
  headless, YOLO26n ONNX downloaded at build) via a Lambda container
  image + Lambda Web Adapter or Mangum; cold start for OpenCV import
  (1–2 s locally, unmeasured on Lambda) must be measured and reported,
  not assumed away

## Decision needed from Olly

1. Accept ~$10–$15 App Runner for the judging window (original plan,
   stateful, no rework), with a billing alarm and a delete date after
   10 Nov — this is NOT zero cost.
2. Accept Lambda rework (stateless + session store, or demo-only) to
   stay inside the always-free tier — this IS closest to zero cost, but
   it is not built or tested yet, and it needs an AWS account connected.
3. Submit with a live screen-share fallback instead of a live endpoint
   (allowed as "or arranged live screen-share" in the competition
   requirements as found) — no AWS cost, but weaker for judges.

No AWS account is connected to Muse in this workspace, and no AWS
service has been started. Any deploy needs Olly's AWS account access
first, plus the GitHub push fix (403, see repo status).
