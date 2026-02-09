from __future__ import annotations

import argparse
import json
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train YOLOv8 on SARFish")
    p.add_argument("--data", required=True, help="dataset.yaml path")
    p.add_argument("--model", default="yolov8n.pt", help="Pretrained model")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=-1)
    p.add_argument("--project", default="runs")
    p.add_argument("--name", default="sarfish")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        project=args.project,
        name=args.name,
    )

    save_dir = Path(model.trainer.save_dir)
    best_src = save_dir / "weights" / "best.pt"
    best_dst = Path("models/weights/best.pt")
    best_dst.parent.mkdir(parents=True, exist_ok=True)
    if best_src.exists():
        best_dst.write_bytes(best_src.read_bytes())

    summary = {}
    results_csv = save_dir / "results.csv"
    if results_csv.exists():
        lines = results_csv.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) >= 2:
            header = [h.strip() for h in lines[0].split(",")]
            last = [v.strip() for v in lines[-1].split(",")]
            row = dict(zip(header, last))
            summary = {
                "precision": float(row.get("metrics/precision(B)", 0.0)),
                "recall": float(row.get("metrics/recall(B)", 0.0)),
                "map50": float(row.get("metrics/mAP50(B)", 0.0)),
                "map5095": float(row.get("metrics/mAP50-95(B)", 0.0)),
            }

    summary_path = Path("runs/summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Best weights: {best_dst}")
    print(f"Summary saved: {summary_path}")


if __name__ == "__main__":
    main()
