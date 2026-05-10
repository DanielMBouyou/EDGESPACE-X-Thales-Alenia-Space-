from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header, metric_card
from app.utils import ROOT
from src.infer.event_packet import make_event_packet
from src.infer.runtime import model_size_mb
from src.utils.hashing import sha256_bytes

st.set_page_config(page_title="EDGE SPACE — KPIs", layout="wide")
apply_theme()
init_state()

header("KPIs", "Key metrics: latency, accuracy, payload footprint.")

st.write("")

# ── Métriques du modèle ──────────────────────────────────────────────────────
st.markdown("### Model metrics")

summary_path = ROOT / "runs" / "summary.json"
summary: dict = {}
if summary_path.exists():
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        summary = {}

# Also look for latest training run
runs_dir = ROOT / "runs" / "detect" / "runs"
if not summary and runs_dir.exists():
    for rd in sorted(runs_dir.iterdir(), reverse=True):
        results_csv = rd / "results.csv"
        if results_csv.exists():
            try:
                df = pd.read_csv(results_csv)
                df.columns = df.columns.str.strip()
                last = df.iloc[-1]
                summary = {
                    "precision": float(last.get("metrics/precision(B)", 0)),
                    "recall": float(last.get("metrics/recall(B)", 0)),
                    "map50": float(last.get("metrics/mAP50(B)", 0)),
                    "map5095": float(last.get("metrics/mAP50-95(B)", 0)),
                    "epochs": len(df),
                }
            except Exception:
                pass
            break

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Precision", f"{summary.get('precision', 0):.3f}")
with c2:
    st.metric("Recall", f"{summary.get('recall', 0):.3f}")
with c3:
    st.metric("mAP@50", f"{summary.get('map50', 0):.3f}")
with c4:
    st.metric("mAP@50-95", f"{summary.get('map5095', 0):.3f}")

if summary.get("epochs"):
    st.caption(f"After {summary['epochs']} training epochs")

st.divider()

# ── Empreinte payload ─────────────────────────────────────────────────────────
st.markdown("### Payload footprint")

weights_pt = ROOT / "models" / "weights" / "best.pt"
onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"

model_rows = []
for name, path in [
    ("best.pt (PyTorch)", weights_pt),
    ("best.onnx (FP32)", onnx_fp32),
    ("best.int8.onnx (INT8)", onnx_int8),
]:
    if path.exists():
        size = model_size_mb(path)
        model_rows.append({
            "Model": name,
            "Size (MB)": f"{size:.2f}",
            "Orbital ready": "Yes" if "onnx" in name else "No (too heavy)",
        })

if model_rows:
    st.table(pd.DataFrame(model_rows))
else:
    st.info("No model found. Training may still be in progress.")

st.divider()

# ── Taille Event Packet ──────────────────────────────────────────────────────
st.markdown("### Event packet size")

dummy_packet = make_event_packet(
    [{"bbox_px": [100, 100, 200, 200], "confidence": 0.92, "class": "fire"}],
    {
        "input_hash": sha256_bytes(b"demo"),
        "image_size": [640, 640],
        "model_name": "yolo11s-fire",
        "model_version": "demo",
        "runtime": "onnx-fp16",
        "latency_ms": {},
    },
    secret="demo-secret",
)
packet_bytes = len(json.dumps(dummy_packet).encode())

pc1, pc2, pc3 = st.columns(3)
with pc1:
    st.metric("Event packet (1 detection)", f"{packet_bytes / 1024:.2f} kB")
with pc2:
    image_size_mb = 50  # typical satellite image
    ratio = image_size_mb * 1024 * 1024 / max(packet_bytes, 1)
    st.metric("Compression ratio", f"×{ratio:,.0f}")
with pc3:
    st.metric("Saved per image", f"{image_size_mb} MB → {packet_bytes / 1024:.1f} kB")

st.divider()

# ── Comparatif volume ─────────────────────────────────────────────────────────
st.markdown("### Data volume — image vs event packet")

st.table(pd.DataFrame({
    "Scenario": [
        "1 image",
        "10 images (one pass)",
        "100 images (one day)",
        "1,000 images (constellation)",
    ],
    "Raw images (MB)": [50, 500, 5_000, 50_000],
    "Event packets (kB)": [
        f"{packet_bytes/1024:.1f}",
        f"{10*packet_bytes/1024:.1f}",
        f"{100*packet_bytes/1024:.1f}",
        f"{1000*packet_bytes/1024:.1f}",
    ],
    "Reduction": ["99.998 %"] * 4,
}))

st.divider()

# ── Budget latence ────────────────────────────────────────────────────────────
st.markdown("### Latency budget — orbit to alert")

st.table(pd.DataFrame({
    "Step": [
        "T_infer (on-board inference)",
        "T_buffer (contact wait)",
        "T_downlink (transmission)",
        "T_api (webhook)",
        "Total P50",
        "Total P95",
    ],
    "LP (Low Power)": ["800 ms", "~300 s (worst case)", "< 1 s", "< 1 s", "~5 min", "~12 min"],
    "HP (High Perf)": ["50 ms", "~300 s (worst case)", "< 1 s", "< 1 s", "~5 min", "~12 min"],
    "HP + GEO relay": ["50 ms", "~10 s", "< 1 s", "< 1 s", "< 15 sec", "< 60 sec"],
}))

st.caption("The bottleneck is T_buffer (contact-window wait), not inference.")
