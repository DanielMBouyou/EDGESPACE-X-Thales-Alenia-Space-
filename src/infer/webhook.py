from __future__ import annotations

import time
from typing import Any, Dict, Tuple

import requests


def post_webhook(
    url: str,
    packet: Dict[str, Any],
    timeout: int = 5,
    retries: int = 3,
) -> Tuple[int, str, float]:
    last_status = 0
    last_body = ""
    start = time.perf_counter()
    for attempt in range(retries):
        try:
            resp = requests.post(
                url,
                json=packet,
                timeout=timeout,
                headers={"Idempotency-Key": packet.get("event_id", "")},
            )
            last_status = resp.status_code
            last_body = resp.text[:500]
            break
        except requests.RequestException as exc:
            last_status = 0
            last_body = str(exc)
            time.sleep(0.3)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return last_status, last_body, elapsed_ms
