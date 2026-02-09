from __future__ import annotations

from pathlib import Path
import onnxruntime as ort
from ultralytics import YOLO


def model_size_mb(path: str | Path) -> float:
    p = Path(path)
    if not p.exists():
        return 0.0
    return p.stat().st_size / (1024 * 1024)


def load_onnx_session(path: str) -> ort.InferenceSession:
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])


def load_pt_model(path: str) -> YOLO:
    return YOLO(path)
