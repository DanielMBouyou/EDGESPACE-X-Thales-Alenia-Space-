from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Dict, Generator


@contextmanager
def timing(bucket: Dict[str, float], key: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    bucket[key] = (end - start) * 1000.0
