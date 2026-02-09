from __future__ import annotations

import uuid
from typing import Any, Dict, List

from src.utils.hashing import canonical_json, hmac_sha256, now_utc_iso, sha256_bytes


def make_event_packet(
    detections: List[Dict[str, Any]],
    meta: Dict[str, Any],
    secret: str,
) -> Dict[str, Any]:
    event_id = str(uuid.uuid4())
    packet = {
        "event_id": event_id,
        "event_type": meta.get("event_type", "wildfire"),
        "timestamp_utc": now_utc_iso(),
        "sat_id": meta.get("sat_id", "EDGESPACE-SIM-01"),
        "sensor_mode": meta.get("sensor_mode", "Optical/IR"),
        "geolocation": meta.get("geolocation", {"lat": 0.0, "lon": 0.0, "geohash": "unknown"}),
        "detections": detections,
        "evidence": {
            "thumbnail_b64": meta.get("thumbnail_b64", ""),
            "thumbnail_hash": meta.get("thumbnail_hash", ""),
        },
        "input": {
            "input_hash": meta.get("input_hash"),
            "image_size": meta.get("image_size"),
            "tile_index": meta.get("tile_index", 0),
        },
        "model": {
            "model_name": meta.get("model_name", "yolov8"),
            "model_version": meta.get("model_version"),
            "runtime": meta.get("runtime"),
        },
        "latency_ms": meta.get("latency_ms", {}),
        "integrity": {
            "packet_hash": "",
            "signature": "",
        },
    }

    packet_for_hash = dict(packet)
    packet_for_hash["integrity"] = {"packet_hash": "", "signature": ""}
    packet_hash = sha256_bytes(canonical_json(packet_for_hash).encode("utf-8"))
    signature = hmac_sha256(secret, packet_hash)

    packet["integrity"]["packet_hash"] = packet_hash
    packet["integrity"]["signature"] = signature

    return packet
