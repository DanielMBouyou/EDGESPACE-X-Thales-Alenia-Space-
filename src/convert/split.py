from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path
from typing import List

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Split YOLO dataset into train/val")
    p.add_argument("--yolo", required=True, help="YOLO dataset root (datasets/yolo)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--train-ratio", type=float, default=0.8)
    p.add_argument("--move", action="store_true", help="Move instead of copy")
    return p.parse_args()


def list_images(folder: Path) -> List[Path]:
    return [p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS]


def main() -> None:
    args = parse_args()
    root = Path(args.yolo)
    images_all = root / "images" / "all"
    labels_all = root / "labels" / "all"

    if images_all.exists():
        images = list_images(images_all)
    else:
        images = list_images(root / "images")
        labels_all = root / "labels"

    if not images:
        raise FileNotFoundError("No images found to split.")

    random.seed(args.seed)
    random.shuffle(images)
    split_idx = int(len(images) * args.train_ratio)
    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    for subset, subset_images in (("train", train_imgs), ("val", val_imgs)):
        out_img = root / "images" / subset
        out_lbl = root / "labels" / subset
        out_img.mkdir(parents=True, exist_ok=True)
        out_lbl.mkdir(parents=True, exist_ok=True)

        for img_path in subset_images:
            lbl_path = labels_all / f"{img_path.stem}.txt"
            target_img = out_img / img_path.name
            target_lbl = out_lbl / lbl_path.name

            if args.move:
                shutil.move(str(img_path), str(target_img))
                if lbl_path.exists():
                    shutil.move(str(lbl_path), str(target_lbl))
                else:
                    target_lbl.write_text("", encoding="utf-8")
            else:
                shutil.copy2(img_path, target_img)
                if lbl_path.exists():
                    shutil.copy2(lbl_path, target_lbl)
                else:
                    target_lbl.write_text("", encoding="utf-8")

    dataset_yaml = root.parent / "dataset.yaml"
    dataset_yaml.write_text(
        "path: datasets/yolo\ntrain: images/train\nval: images/val\nnames: ['vessel']\n",
        encoding="utf-8",
    )

    print(f"Split complete. Train: {len(train_imgs)} | Val: {len(val_imgs)}")


if __name__ == "__main__":
    main()
