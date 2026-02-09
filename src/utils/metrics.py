from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def percentiles(values: Iterable[float], p50: float = 50, p95: float = 95) -> Tuple[float, float]:
    arr = np.array(list(values), dtype=float)
    if arr.size == 0:
        return 0.0, 0.0
    return float(np.percentile(arr, p50)), float(np.percentile(arr, p95))
