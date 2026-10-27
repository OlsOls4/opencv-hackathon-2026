# Deploying the demo-only landing page to Lambda

File: `lambda_demo_page.html` (self-contained: inline CSS and JS, system
fonts only, no CDN, no external paid service).

Live demo-only endpoint today: the AWS Lambda Function URL
`https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/`
returns JSON only. This page replaces only the root response.

## What must NOT change

- `GET /health` — same JSON as today.
- `GET /api/demo` — same JSON as today (staged Gap, changed 0.625,
  3 synthetic items vs full baseline 8).
- Do not add a webcam, OpenCV, counting, upload, or baseline route
  to this function. Those live only in the full EC2 app.

## Handler change (in `lambda_demo.py`)

Read `lambda_demo_page.html` into a module-level constant (for
example `LANDING_HTML`, loaded once at import from a file bundled
in the deployment zip), then in `handler()`:

```python
if path in ("/", ""):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": LANDING_HTML,
    }
```

Keep every other branch exactly as it is today. Redeploy the
function (same function `shelfscan-demo`, eu-north-1, Python 3.14),
then verify, in order:

1. Root URL returns HTML and shows the hero, the demo-only notice,
   and the live demo state fetched from `./api/demo`.
2. `/health` still returns JSON, not HTML.
3. `/api/demo` still returns JSON (Gap, 0.625), not HTML.
4. The page on a phone-width viewport still shows the hero, CTAs,
   and state cards without horizontal scrolling.

## Value correction — read before deploying

The task brief said to show "Low, changed 0.216" on this page.
That figure is the **full EC2 app's** `/api/demo`, not the Lambda
demo-only `/api/demo` (which is Gap, 0.625, staged). This page
therefore does NOT hardcode Low / 0.216 as a Lambda result. It
fetches `./api/demo` live and shows whatever it returns, and it
shows Low / 0.216 in a separate, clearly labelled EC2 card. If a
reviewer hardcodes Low / 0.216 onto the Lambda page, that page
would contradict its own `/api/demo` JSON. Keep the two figures
separated as built.
