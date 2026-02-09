from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header
from app.utils import ROOT
from src.infer.event_packet import make_event_packet
from src.infer.predict_onnx import predict_onnx
from src.infer.predict_pt import predict_pt
from src.infer.runtime import load_onnx_session, load_pt_model, model_size_mb
from src.utils.hashing import sha256_bytes
from src.utils.image import load_image_from_bytes
from src.utils.metrics import percentiles

st.set_page_config(page_title="EDGE SPACE - KPIs", layout="wide")
apply_theme()
init_state()

header("KPIs", "Latency, accuracy, and payload footprint.")

summary_path = ROOT / "runs" / "summary.json"
summary = {}
if summary_path.exists():
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        summary = {}

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Precision", f"{summary.get('precision', 0):.3f}")
with col2:
    st.metric("Recall", f"{summary.get('recall', 0):.3f}")
with col3:
    st.metric("mAP50-95", f"{summary.get('map5095', 0):.3f}")

st.divider()

@st.cache_resource
def get_pt_model(path: str):
    return load_pt_model(path)


@st.cache_resource
def get_onnx_session(path: str):
    return load_onnx_session(path)


mode = st.radio("Runtime", ["Orbite (ONNX)", "Sol (PT)"], horizontal=True)
run_batch = st.button("Run batch test (demo_samples)")

latencies = []
if run_batch:
    sample_dir = ROOT / "datasets" / "demo_samples"
    samples = sorted([p for p in sample_dir.glob("*.*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}])
    if not samples:
        st.warning("No demo samples found in datasets/demo_samples.")
    else:
        if mode.startswith("Orbite"):
            onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
            onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
            onnx_path = onnx_int8 if onnx_int8.exists() else onnx_fp32
            if not onnx_path.exists():
                st.error("Missing ONNX model.")
            else:
                session = get_onnx_session(str(onnx_path))
                input_name = session.get_inputs()[0].name
                for p in samples[:50]:
                    img = load_image_from_bytes(p.read_bytes())
                    _, t = predict_onnx(img, session=session, input_name=input_name)
                    latencies.append(sum(t.values()))
        else:
            weights = ROOT / "models" / "weights" / "best.pt"
            if not weights.exists():
                st.error("Missing PT model.")
            else:
                model = get_pt_model(str(weights))
                for p in samples[:50]:
                    img = load_image_from_bytes(p.read_bytes())
                    _, t = predict_pt(img, model=model)
                    latencies.append(sum(t.values()))

if latencies:
    p50, p95 = percentiles(latencies)
    st.metric("Latency P50", f"{p50:.1f} ms")
    st.metric("Latency P95", f"{p95:.1f} ms")
    st.line_chart(pd.DataFrame({"latency_ms": latencies}))

st.divider()

weights = ROOT / "models" / "weights" / "best.pt"
onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"

st.markdown("**Model size**")
model_rows = []
if weights.exists():
    model_rows.append({"model": "best.pt", "size_mb": model_size_mb(weights)})
if onnx_fp32.exists():
    model_rows.append({"model": "best.onnx", "size_mb": model_size_mb(onnx_fp32)})
if onnx_int8.exists():
    model_rows.append({"model": "best.int8.onnx", "size_mb": model_size_mb(onnx_int8)})
if model_rows:
    st.table(pd.DataFrame(model_rows))
else:
    st.info("No model files found.")

st.markdown("**Packet size (kB)**")
packet = st.session_state.last_packet
if packet is None:
    packet = make_event_packet(
        [],
        {
            "input_hash": sha256_bytes(b""),
            "image_size": [640, 640],
            "model_name": "yolov8",
            "model_version": "demo",
            "runtime": "onnx-int8",
            "latency_ms": {},
        },
        secret="demo-secret",
    )
packet_size_kb = len(json.dumps(packet).encode("utf-8")) / 1024
st.metric("Event packet size", f"{packet_size_kb:.2f} kB")
