# Lambda demo — reproducibility note

## What is live

- Function: `shelfscan-demo`, region `eu-north-1`, runtime Python 3.14.
- Public Function URL, auth NONE:
  `https://rhy7elxmanwrtyuqyfw2xg53ji0bnecg.lambda-url.eu-north-1.on.aws/`
- Only `GET /health` and `GET /api/demo` are exposed.

## What `lambda_demo.py` reproduces

`lambda_demo.py` (repo root, standard library only, single-file zip)
is the code for that demo endpoint. It reproduces:

- `/health`:
  `{"status":"ok","service":"ShelfScan","mode":"lambda-demo","model":"yolo26n.onnx","opencv":"not-loaded-in-lambda-demo"}`
- `/api/demo`: staged synthetic sparse shelf, total 3, state `Gap`,
  `changed_ratio` 0.625 (= (8 − 3) / 8, full baseline 8 items),
  `annotated_image_base64` null, counts `{"synthetic-item": 3}`.

Local check, no AWS and no dependencies:

```bash
python lambda_demo.py
python -m pytest tests/test_lambda_demo.py -q
```

Deploy (manual, not done from this repo): create function
`shelfscan-demo` in eu-north-1 with Python 3.14, handler
`lambda_demo.handler`, upload `lambda_demo.py` as a zip, enable a
Function URL with auth NONE, then check `/health` and `/api/demo`.

## What it does not reproduce

This is the demo endpoint only, not the full ShelfScan app. OpenCV
is not loaded in Lambda, there is no live webcam, no stateful
tracking, no `/api/frame`, no upload, no baseline capture, and no
annotated image. The full FastAPI + OpenCV 5 app still requires
running this repo locally — see README "How to run". The local
`/api/demo` differs by design (real drift code on synthetic images:
state Low, total 0); do not present either demo result as a real
shelf count, and do not present local latency figures as Lambda
figures — none has been measured on Lambda.

## Remaining gap

The live function was deployed from code outside this repo; this file
is a faithful reproduction of its observed responses, not a byte-for-byte
copy of the originally deployed source. The Function URL will be
disabled/deleted after judging.
