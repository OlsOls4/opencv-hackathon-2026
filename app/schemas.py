"""Single result shape used by every API route, so judges can compare outputs."""
from collections import Counter


def result_shape(counts, total, tracks, latency_ms, model, threshold, state=None, changed_ratio=None, annotated_b64=None):
    return {
        "counts": dict(counts),
        "total": total,
        "tracks": tracks,
        "latency_ms": round(float(latency_ms), 1),
        "model": model,
        "threshold": threshold,
        "state": state,
        "changed_ratio": changed_ratio,
        "annotated_image_base64": annotated_b64,
    }


def counts_from_detections(detections):
    return Counter(d["label"] for d in detections)
