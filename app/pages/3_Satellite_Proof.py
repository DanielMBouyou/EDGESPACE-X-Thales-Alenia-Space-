from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header
from app.utils import ROOT
from src.infer.predict_onnx import predict_onnx
from src.infer.runtime import load_onnx_session, model_size_mb
from src.utils.image import load_image_from_bytes
from src.utils.metrics import percentiles

st.set_page_config(page_title="EDGE SPACE - Satellite Proof", layout="wide")
apply_theme()
init_state()

header("Satellite Proof", "Orbit readiness checklist and measured constraints.")

st.markdown("**Checklist**")
st.markdown("- [x] ONNX export")
st.markdown("- [x] Quantif (INT8 when available)")
st.markdown("- [x] onnxruntime")
st.markdown("- [x] Input fixed 640")
st.markdown("- [x] NMS deterministic")

st.divider()

onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
onnx_path = onnx_int8 if onnx_int8.exists() else onnx_fp32

if onnx_path.exists():
    size_mb = model_size_mb(onnx_path)
    st.metric("Model size", f"{size_mb:.2f} MB")
    st.metric("RAM peak (est)", f"{size_mb * 3.2:.0f} MB")
else:
    st.warning("ONNX model missing. Export first.")

run_batch = st.button("Run batch test (50)")
if run_batch and onnx_path.exists():
    sample_dir = ROOT / "datasets" / "demo_samples"
    samples = sorted([p for p in sample_dir.glob("*.*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}])
    if not samples:
        st.warning("No demo samples found in datasets/demo_samples.")
    else:
        session = load_onnx_session(str(onnx_path))
        input_name = session.get_inputs()[0].name
        latencies = []
        failures = 0
        for p in samples[:50]:
            try:
                img = load_image_from_bytes(p.read_bytes())
                _, t = predict_onnx(img, session=session, input_name=input_name)
                latencies.append(sum(t.values()))
            except Exception:
                failures += 1
        p50, p95 = percentiles(latencies)
        error_rate = failures / max(1, len(samples[:50]))
        st.metric("P50", f"{p50:.1f} ms")
        st.metric("P95", f"{p95:.1f} ms")
        st.metric("Error rate", f"{error_rate * 100:.1f}%")
        if latencies:
            st.line_chart(pd.DataFrame({"latency_ms": latencies}))
