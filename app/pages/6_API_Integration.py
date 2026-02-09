from __future__ import annotations

import json

import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE - API Integration", layout="wide")
apply_theme()
init_state()

header("API Integration", "Event packet schema and example webhook call.")

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "EventPacket",
    "type": "object",
    "required": ["event_id", "event_type", "timestamp_utc", "sensor_mode", "detections", "input", "model", "integrity"],
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "timestamp_utc": {"type": "string"},
        "sensor_mode": {"type": "string"},
        "detections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "bbox_px": {"type": "array", "items": {"type": "number"}},
                    "confidence": {"type": "number"},
                    "class": {"type": "string"},
                },
            },
        },
        "input": {
            "type": "object",
            "properties": {
                "input_hash": {"type": "string"},
                "image_size": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
            },
        },
        "model": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string"},
                "model_version": {"type": "string"},
                "runtime": {"type": "string"},
            },
        },
        "integrity": {
            "type": "object",
            "properties": {
                "packet_hash": {"type": "string"},
                "signature": {"type": "string"},
            },
        },
        "latency_ms": {"type": "object"},
    },
}

st.markdown("**JSON Schema**")
st.code(json.dumps(schema, indent=2), language="json")

st.markdown("**Example curl**")
st.code(
    """
curl -X POST https://client.example.com/webhook \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: <event_id>" \
  -d @event_packet.json
""",
    language="bash",
)
