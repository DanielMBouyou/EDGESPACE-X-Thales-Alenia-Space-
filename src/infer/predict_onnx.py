from __future__ import annotations

import argparse
from typing import Dict, List, Tuple

import numpy as np
import onnxruntime as ort
from PIL import Image

from src.utils.image import image_to_tensor, load_image, resize_to_square
from src.utils.nms import nms
from src.utils.timing import timing


def decode_outputs(pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # Expect shape (1, C, N) or (1, N, C)
    if pred.ndim != 3:
        raise ValueError(f"Unexpected output shape: {pred.shape}")

    if pred.shape[1] < pred.shape[2]:
        pred = np.transpose(pred, (0, 2, 1))  # (1, N, C)
    pred = pred[0]

    boxes = pred[:, :4]
    scores = pred[:, 4:]

    if scores.shape[1] == 1:
        conf = scores[:, 0]
        cls = np.zeros_like(conf, dtype=int)
    else:
        cls = np.argmax(scores, axis=1)
        conf = scores[np.arange(scores.shape[0]), cls]

    return boxes, conf


def xywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
    x, y, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    x1 = x - w / 2
    y1 = y - h / 2
    x2 = x + w / 2
    y2 = y + h / 2
    return np.stack([x1, y1, x2, y2], axis=1)


def predict_onnx(
    image: Image.Image,
    model_path: str | None = None,
    session: ort.InferenceSession | None = None,
    input_name: str | None = None,
    conf_thres: float = 0.25,
    iou_thres: float = 0.5,
) -> Tuple[List[Dict], Dict[str, float]]:
    timings: Dict[str, float] = {}

    with timing(timings, "preprocess"):
        orig_w, orig_h = image.size
        resized = resize_to_square(image, 640)
        tensor = image_to_tensor(resized)

    with timing(timings, "inference"):
        if session is None:
            if model_path is None:
                raise ValueError("model_path is required when session is not provided")
            session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        if input_name is None:
            input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: tensor})
        pred = outputs[0]

    with timing(timings, "postprocess"):
        boxes, conf = decode_outputs(pred)
        boxes_xyxy = xywh_to_xyxy(boxes)

        mask = conf >= conf_thres
        boxes_xyxy = boxes_xyxy[mask]
        conf = conf[mask]

        if boxes_xyxy.size == 0:
            return [], timings

        keep = nms(boxes_xyxy, conf, iou_threshold=iou_thres)
        boxes_xyxy = boxes_xyxy[keep]
        conf = conf[keep]

        scale_x = orig_w / 640.0
        scale_y = orig_h / 640.0
        detections: List[Dict] = []
        for (x1, y1, x2, y2), score in zip(boxes_xyxy, conf):
            bbox = [
                float(max(0.0, x1 * scale_x)),
                float(max(0.0, y1 * scale_y)),
                float(min(orig_w, x2 * scale_x)),
                float(min(orig_h, y2 * scale_y)),
            ]
            detections.append({"bbox_px": bbox, "confidence": float(score), "class": "vessel"})

    return detections, timings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ONNX inference")
    p.add_argument("--image", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.5)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    image = load_image(args.image)
    detections, timings = predict_onnx(image, args.model, args.conf, args.iou)
    print(f"Detections: {len(detections)}")
    print(detections[:3])
    print(timings)


if __name__ == "__main__":
    main()
