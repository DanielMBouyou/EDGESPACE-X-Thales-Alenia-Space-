from __future__ import annotations

from io import BytesIO
from typing import Iterable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw


def load_image_from_bytes(data: bytes) -> Image.Image:
    img = Image.open(BytesIO(data)).convert("RGB")
    return img


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def resize_to_square(img: Image.Image, size: int = 640) -> Image.Image:
    return img.resize((size, size), Image.BILINEAR)


def image_to_tensor(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img).astype(np.float32) / 255.0
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    arr = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(arr, axis=0)


def draw_bboxes(
    img: Image.Image,
    boxes: Iterable[Tuple[float, float, float, float]],
    labels: Iterable[str],
    color: Tuple[int, int, int] = (0, 255, 160),
    width: int = 2,
) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    for (x1, y1, x2, y2), label in zip(boxes, labels):
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
        if label:
            draw.text((x1 + 3, max(0, y1 - 14)), label, fill=color)
    return out


def as_rgb_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
