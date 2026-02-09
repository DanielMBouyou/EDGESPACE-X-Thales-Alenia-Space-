from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export YOLOv8 model to ONNX")
    p.add_argument("--weights", required=True, help="Path to .pt weights")
    p.add_argument("--out", default=None, help="Output ONNX path")
    p.add_argument("--imgsz", type=int, default=640)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model = YOLO(args.weights)
    export_path = model.export(format="onnx", imgsz=args.imgsz, simplify=True)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        Path(export_path).replace(out_path)
        print(f"Exported to {out_path}")
    else:
        print(f"Exported to {export_path}")


if __name__ == "__main__":
    main()
