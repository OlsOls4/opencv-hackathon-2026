# Third-party notices

Olly's own code is MIT (see LICENSE). The following are separate and are
NOT covered by that MIT file:

- **OpenCV 5** — BSD-style licence, see https://opencv.org/license/
- **YOLO26n model weights / ONNX export** — Ultralytics, official v8.4.0
  release asset yolo26n.onnx, SHA256 in MODEL_CARD.md. Check the Ultralytics
  licence for the model at export/download time; do not assume MIT covers it.
- **COCO class names (models/coco80.json)** — COCO dataset, CC BY 4.0.
- **HoloSelecta (evaluation only, if used)** — CC BY 4.0, cite Fuchs et al.,
  Data in Brief 32 (2020) 106280. Vending-domain transfer, not a shelf proxy.
- **SKU-110K (appendix stress test only, if used)** — academic /
  non-commercial use only, proprietary licence by Trax. Single class only;
  never report it as label accuracy, and do not redistribute it under MIT.
- **RPC, MVTec D2S, Freiburg, Grozi, KTH** — licences NOT verified at v1
  build time; do not use or redistribute until verified (see docs/EVALUATION.md).

No dataset, photo, or model is redistributed under MIT in this repo.
