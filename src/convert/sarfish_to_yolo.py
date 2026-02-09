from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from PIL import Image

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def find_images(root: Path) -> List[Path]:
    return [p for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXTS]


def find_first_annotation(root: Path) -> Path | None:
    for ext in (".csv", ".json"):
        hits = list(root.rglob(f"*{ext}"))
        if hits:
            return hits[0]
    return None


def pick_col(df: pd.DataFrame, candidates: List[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert SARFish annotations to YOLO format")
    p.add_argument("--input", required=True, help="Root folder containing images and annotations")
    p.add_argument("--output", required=True, help="Output YOLO dataset folder (datasets/yolo)")
    p.add_argument("--images", default=None, help="Optional images folder override")
    p.add_argument("--annotations", default=None, help="Optional annotations file override")
    p.add_argument("--class-id", type=int, default=0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_root = Path(args.input)
    out_root = Path(args.output)

    images_dir = Path(args.images) if args.images else in_root
    ann_path = Path(args.annotations) if args.annotations else find_first_annotation(in_root)
    if ann_path is None:
        raise FileNotFoundError("No annotation file found. Use --annotations to specify one.")

    images = find_images(images_dir)
    if not images:
        raise FileNotFoundError("No images found. Use --images to specify an image folder.")

    index_by_stem = {p.stem: p for p in images}
    index_by_name = {p.name: p for p in images}

    if ann_path.suffix.lower() == ".csv":
        df = pd.read_csv(ann_path)
    else:
        df = pd.read_json(ann_path)

    image_col = pick_col(
        df,
        ["image_id", "image", "image_name", "filename", "file_name", "name", "chip_id", "scene_id"],
    ) or df.columns[0]
    x_col = pick_col(df, ["x", "x_min", "xmin", "bbox_xmin", "left"])
    y_col = pick_col(df, ["y", "y_min", "ymin", "bbox_ymin", "top"])
    w_col = pick_col(df, ["w", "width", "bbox_width", "bbox_w"])
    h_col = pick_col(df, ["h", "height", "bbox_height", "bbox_h"])
    x2_col = pick_col(df, ["x_max", "xmax", "right"])
    y2_col = pick_col(df, ["y_max", "ymax", "bottom"])

    if x_col is None or y_col is None or (w_col is None and (x2_col is None)) or (h_col is None and (y2_col is None)):
        raise ValueError("Could not find bbox columns. Provide a CSV with x/y/width/height or x_max/y_max.")

    out_images = out_root / "images" / "all"
    out_labels = out_root / "labels" / "all"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    annotations: Dict[Path, List[Tuple[float, float, float, float]]] = defaultdict(list)

    for row in df.itertuples(index=False):
        image_id = str(getattr(row, image_col))
        image_name = Path(image_id).name
        image_stem = Path(image_id).stem
        img_path = index_by_name.get(image_name) or index_by_stem.get(image_stem)
        if img_path is None:
            continue

        x1 = float(getattr(row, x_col))
        y1 = float(getattr(row, y_col))
        if w_col:
            w = float(getattr(row, w_col))
            h = float(getattr(row, h_col))
            x2 = x1 + w
            y2 = y1 + h
        else:
            x2 = float(getattr(row, x2_col))
            y2 = float(getattr(row, y2_col))
            w = x2 - x1
            h = y2 - y1

        if w <= 1 or h <= 1:
            continue

        annotations[img_path].append((x1, y1, x2, y2))

    for img_path, boxes in annotations.items():
        with Image.open(img_path) as img:
            w, h = img.size
        label_lines = []
        for x1, y1, x2, y2 in boxes:
            x1 = max(0.0, min(float(w), x1))
            y1 = max(0.0, min(float(h), y1))
            x2 = max(0.0, min(float(w), x2))
            y2 = max(0.0, min(float(h), y2))
            bw = max(1.0, x2 - x1)
            bh = max(1.0, y2 - y1)
            xc = (x1 + bw / 2.0) / w
            yc = (y1 + bh / 2.0) / h
            bw_n = bw / w
            bh_n = bh / h
            label_lines.append(f"{args.class_id} {xc:.6f} {yc:.6f} {bw_n:.6f} {bh_n:.6f}")

        out_img = out_images / img_path.name
        out_lbl = out_labels / f"{img_path.stem}.txt"
        shutil.copy2(img_path, out_img)
        out_lbl.write_text("\n".join(label_lines) + "\n", encoding="utf-8")

    print(f"Converted {len(annotations)} images to YOLO format in {out_root}")


if __name__ == "__main__":
    main()
