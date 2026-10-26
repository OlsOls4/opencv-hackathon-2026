# Deployment — SUPERSEDED App Runner plan + live Lambda demo

> Deployment status, 26 Oct 2026: the live judge link is a demo-only AWS
> Lambda function in eu-north-1 exposing /health and /api/demo only,
> with OpenCV NOT loaded. The App Runner eu-west-2 design below is
> superseded and was not deployed as drawn — App Runner eu-west-2 was
> unavailable and Lambda eu-west-2 was region-blocked for this account.
> The full FastAPI + OpenCV 5 app runs from this repo locally only.
> The Lambda demo code is not in this repo, so the live endpoint cannot
> be rebuilt from this repo alone. Do not submit the App Runner diagram
> as the deployed architecture without updating it to the Lambda demo.

# Deployment — AWS App Runner (prepared only, NOT deployed)

1. Olly creates/verifies an AWS account, payment method, and billing alarm
   ($10-$20 suggested).
2. Push this repo to GitHub (Olly owns repo creation/authorisation).
3. Create an App Runner service in eu-west-2 from the repo, 2 vCPU / 4 GB,
   port 8000, health check /health.
4. Test /health and /api/demo incognito from a second device/browser.
5. Record actual App Runner config + observed cost/latency in results/latency.md
   — do not quote a fake exact price in the submission.
6. After Devpost submission: disable auto-deploy / pin to the submitted
   commit, so a later push cannot break judges' endpoint.
7. Keep the endpoint live 27 Oct-10 Nov: named owner, cost cap, health
   check at least every few days, immediate check if a judge reports failure.
   A billing alarm alone is not a keep-alive plan.
8. Fallback (only if App Runner cannot run the container or is too slow
   after one CPU-size increase): same Dockerfile on a single EC2/Lightsail
   instance with Docker + reverse proxy for HTTPS.

No live webcam frames go to S3 by default; only an explicit Save snapshot
action stores an annotated image, and only in the session.
