from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header
from src.infer.webhook import post_webhook

st.set_page_config(page_title="EDGE SPACE — API", page_icon="📡", layout="wide")
apply_theme()
init_state()

header("📡 API & Webhook", "Schéma JSON, test webhook, logs HTTP.")

st.write("")

# ── JSON Schema ───────────────────────────────────────────────────────────────
st.markdown("### 📋 Schéma Event Packet")

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "EdgeSpaceEventPacket",
    "type": "object",
    "required": [
        "event_id", "event_type", "timestamp_utc", "sat_id", "sensor_mode",
        "geolocation", "detections", "evidence", "input", "model", "integrity",
    ],
    "properties": {
        "event_id": {"type": "string", "format": "uuid"},
        "event_type": {
            "type": "string",
            "enum": ["wildfire", "oil_spill", "vessel", "infra_anomaly"],
        },
        "timestamp_utc": {"type": "string", "format": "date-time"},
        "sat_id": {"type": "string"},
        "sensor_mode": {"type": "string", "enum": ["Optical/IR", "SAR", "Multi-spectral"]},
        "geolocation": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "geohash": {"type": "string"},
            },
        },
        "detections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "bbox_px": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "class": {"type": "string"},
                },
            },
        },
        "evidence": {
            "type": "object",
            "properties": {
                "thumbnail_b64": {"type": "string"},
                "thumbnail_hash": {"type": "string"},
            },
        },
        "input": {
            "type": "object",
            "properties": {
                "input_hash": {"type": "string"},
                "image_size": {"type": "array", "items": {"type": "number"}},
                "tile_index": {"type": "integer"},
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
        "latency_ms": {"type": "object"},
        "integrity": {
            "type": "object",
            "properties": {
                "packet_hash": {"type": "string"},
                "signature": {"type": "string"},
            },
        },
    },
}

st.code(json.dumps(schema, indent=2), language="json")

st.divider()

# ── Webhook test ──────────────────────────────────────────────────────────────
st.markdown("### 🧪 Test Webhook")

webhook_url = st.text_input("URL du webhook", value="http://127.0.0.1:8000/webhook")

col_test, col_mock = st.columns(2)

with col_test:
    st.markdown("**Envoyer le dernier event packet :**")
    if st.session_state.last_packet:
        if st.button("📤 POST webhook"):
            with st.spinner("Envoi…"):
                status, body, latency = post_webhook(webhook_url, st.session_state.last_packet)
            st.session_state.events_log.append({
                "event_id": st.session_state.last_packet["event_id"],
                "status": status,
                "latency_ms": round(latency, 1),
            })
            if 200 <= status < 300:
                st.success(f"✅ HTTP {status} — {latency:.1f} ms")
            else:
                st.error(f"❌ HTTP {status} : {body[:300]}")
                st.session_state.errors_log.append({
                    "event_id": st.session_state.last_packet["event_id"],
                    "error": body[:300],
                })

        st.markdown("**Aperçu payload :**")
        st.code(json.dumps(st.session_state.last_packet, indent=2)[:3000], language="json")
    else:
        st.info("Aucun event packet. Lance d'abord une détection dans « Try it ».")

with col_mock:
    st.markdown("**Serveur mock local :**")
    st.code(
        """# Lancer le serveur mock :
python scripts/mock_webhook.py

# Écoute sur http://127.0.0.1:8000/webhook
# Affiche les packets reçus dans le terminal
""",
        language="bash",
    )

st.divider()

# ── Curl example ──────────────────────────────────────────────────────────────
st.markdown("### 💻 Exemple cURL")

st.code(
    """curl -X POST https://your-server.com/webhook \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: <event_id>" \\
  -d @event_packet.json
""",
    language="bash",
)

st.divider()

# ── HTTP Log ──────────────────────────────────────────────────────────────────
st.markdown("### 📜 Log HTTP")

if st.session_state.events_log:
    st.dataframe(pd.DataFrame(st.session_state.events_log), use_container_width=True)
else:
    st.info("Aucun envoi webhook enregistré.")

if st.session_state.errors_log:
    st.markdown("**❌ Erreurs :**")
    st.dataframe(pd.DataFrame(st.session_state.errors_log), use_container_width=True)
