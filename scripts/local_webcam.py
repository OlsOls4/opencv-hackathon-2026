"""Local-only webcam demo. Uses cv2.VideoCapture(0) on Olly's machine.
This is NOT the AWS path and must not be presented as such.
Press q to quit. Saves annotated frames to results/ if --save is given.
"""
import argparse
import cv2
import sys
sys.path.insert(0, ".")
from app.inference import Detector


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", default="models/yolo26n.onnx")
    args = ap.parse_args()
    det = Detector(args.model)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No webcam available"); return 1
    print("Press q to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        detections, annotated, _ = det.detect(frame)
        cv2.imshow("ShelfScan local webcam (not AWS)", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release(); cv2.destroyAllWindows(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
