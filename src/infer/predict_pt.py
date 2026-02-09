from __future__ import annotations

import argparse
from typing import Dict, List, Tuple

from PIL import Image
from ultralytics import YOLO

from src.utils.image import load_image
from src.utils.timing import timing


def predict_pt(
    image: Image.Image,
    model_path: str | None = None,
    model: YOLO | None = None,
    conf_thres: float = 0.25,
    iou_thres: float = 0.5,
) -> Tuple[List[Dict], Dict[str, float]]:
    timings: Dict[str, float] = {}

    if model is None:
        if model_path is None:
            raise ValueError("model_path is required when model is not provided")
        model = YOLO(model_path)
    timings["preprocess"] = 0.0

    with timing(timings, "inference"):
        results = model.predict(image, conf=conf_thres, iou=iou_thres, imgsz=640, verbose=False)

    with timing(timings, "postprocess"):
        dets: List[Dict] = []
        if results:
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                for box, conf, cls in zip(boxes.xyxy.tolist(), boxes.conf.tolist(), boxes.cls.tolist()):
                    dets.append({"bbox_px": [float(v) for v in box], "confidence": float(conf), "class": "vessel"})

    return dets, timings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PyTorch inference (Ultralytics)")
    p.add_argument("--image", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.5)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    image = load_image(args.image)
    detections, timings = predict_pt(image, args.model, args.conf, args.iou)
    print(f"Detections: {len(detections)}")
    print(detections[:3])
    print(timings)


if __name__ == "__main__":
    main()
