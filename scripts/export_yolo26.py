"""Export recipe for YOLO26n ONNX. RUN ONLY in a separate export env
(requirements-export.txt) — never in the runtime env.

Recipe verified for the committed model:
  model = YOLO("yolo26n.pt")
  model.export(format="onnx", imgsz=640, batch=1, dynamic=False, half=False,
               opset=17, end2end=True, nms=False, device="cpu")
Expected output: [1, 300, 6] — [x1, y1, x2, y2, confidence, class_id].

If Ultralytics/Torch cannot be installed (large download), the committed
model was instead downloaded as the official Ultralytics v8.4.0 release
asset yolo26n.onnx and verified with OpenCV 5 DNN to produce [1, 300, 6].
See download_model.py and MODEL_CARD.md for its SHA256.
"""
import sys


def main():
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ultralytics not installed in this env. Use download_model.py instead.")
        sys.exit(2)
    model = YOLO("yolo26n.pt")
    path = model.export(format="onnx", imgsz=640, batch=1, dynamic=False,
                        half=False, opset=17, end2end=True, nms=False, device="cpu")
    print(f"Exported to {path}")


if __name__ == "__main__":
    main()
