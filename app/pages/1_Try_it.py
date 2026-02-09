from __future__ import annotations

import json
import os
from typing import Dict

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.state import init_state
from app.ui import apply_theme, header, pipeline_bar
from app.utils import ROOT
from src.infer.event_packet import make_event_packet
from src.infer.predict_onnx import predict_onnx
from src.infer.predict_pt import predict_pt
from src.infer.runtime import load_onnx_session, load_pt_model
from src.infer.webhook import post_webhook
from src.utils.hashing import sha256_bytes, sha256_file
from src.utils.image import draw_bboxes, load_image_from_bytes
from src.utils.timing import timing

st.set_page_config(page_title="EDGE SPACE - Try it", layout="wide")
load_dotenv()
apply_theme()
init_state()


@st.cache_resource
def get_pt_model(path: str):
    return load_pt_model(path)


@st.cache_resource
def get_onnx_session(path: str):
    return load_onnx_session(path)

header(
    "Try it",
    "Mode Sol (PyTorch) vs Mode Orbite (ONNX + quantif). Demo complete event packet + webhook.",
)

profiles = {
    "CPU-low": {"ram": "256 MB", "latency": "250 ms"},
    "CPU-mid": {"ram": "512 MB", "latency": "120 ms"},
    "GPU": {"ram": "1.5 GB", "latency": "40 ms"},
}

left, right = st.columns([2, 1])
with left:
    mode = st.radio("Switch Mode", ["Sol (PT)", "Orbite (ONNX + quantif)"], horizontal=True)
    profile = st.selectbox("Profile orbite", list(profiles.keys()))
    st.caption(f"RAM max: {profiles[profile]['ram']} | Latence max: {profiles[profile]['latency']}")

with right:
    st.markdown("**Downlink simulator**")
    transmission = st.selectbox("Transmission", ["Direct GS", "Relay"])
    downlink_delay = st.number_input("Downlink delay (sec)", min_value=0.0, value=3.5, step=0.5)
    queue_delay = st.number_input("Queue delay (sec)", min_value=0.0, value=1.2, step=0.5)
    total_delay = downlink_delay + queue_delay
    st.caption(f"Estimated delivery time: {total_delay:.1f}s ({transmission})")

st.divider()

uploader_col, sample_col = st.columns([2, 1])

with uploader_col:
    uploaded = st.file_uploader("Drag & drop uploader (png/jpg/tif)", type=["png", "jpg", "jpeg", "tif", "tiff"])

with sample_col:
    sample_dir = ROOT / "datasets" / "demo_samples"
    samples = sorted([p for p in sample_dir.glob("*.*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}])
    sample_names = [p.name for p in samples]
    sample_choice = st.selectbox("Try sample", options=sample_names) if sample_names else None
    use_sample = st.button("Use sample") if sample_choice else False
    if samples:
        thumb_cols = st.columns(3)
        for idx, p in enumerate(samples[:6]):
            with thumb_cols[idx % 3]:
                st.image(load_image_from_bytes(p.read_bytes()), caption=p.name, width=120)

image_bytes = None
if uploaded is not None:
    image_bytes = uploaded.getvalue()
elif use_sample and sample_choice:
    sample_path = sample_dir / sample_choice
    image_bytes = sample_path.read_bytes()

if image_bytes:
    st.session_state.last_image = image_bytes

if st.session_state.last_image and image_bytes is None:
    image_bytes = st.session_state.last_image

run = st.button("Run detection")
if run and not image_bytes:
    st.warning("Upload an image or choose a sample first.")

if run and image_bytes:
    image = load_image_from_bytes(image_bytes)
    input_hash = sha256_bytes(image_bytes)

    timings: Dict[str, float] = {}

    if mode.startswith("Sol"):
        weights = ROOT / "models" / "weights" / "best.pt"
        if not weights.exists():
            st.error("Missing models/weights/best.pt. Train a model first.")
            st.stop()
        model = get_pt_model(str(weights))
        detections, det_timings = predict_pt(image, model=model)
        runtime = "pytorch-fp32"
        model_version = sha256_file(weights)
    else:
        onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
        onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
        onnx_path = onnx_int8 if onnx_int8.exists() else onnx_fp32
        if not onnx_path.exists():
            st.error("Missing ONNX model. Export with src/infer/export_onnx.py.")
            st.stop()
        session = get_onnx_session(str(onnx_path))
        input_name = session.get_inputs()[0].name
        detections, det_timings = predict_onnx(image, session=session, input_name=input_name)
        runtime = "onnx-int8" if onnx_path.name.endswith("int8.onnx") else "onnx-fp32"
        model_version = sha256_file(onnx_path)

    timings.update(det_timings)
    with timing(timings, "packaging"):
        packet = make_event_packet(
            detections,
            {
                "input_hash": input_hash,
                "image_size": list(image.size),
                "model_name": "yolov8",
                "model_version": model_version,
                "runtime": runtime,
                "latency_ms": {},
            },
            secret=os.environ.get("EDGE_SPACE_HMAC_SECRET", "demo-secret"),
        )

    timings["total"] = sum(v for k, v in timings.items() if k != "total")
    packet["latency_ms"] = timings

    st.session_state.last_packet = packet
    st.session_state.last_detections = detections
    st.session_state.last_latency = timings

    annotated = draw_bboxes(
        image,
        [d["bbox_px"] for d in detections],
        [f"vessel {d['confidence']:.2f}" for d in detections],
    )
    st.session_state.last_annotated = annotated

if st.session_state.last_packet:
    packet = st.session_state.last_packet
    detections = st.session_state.last_detections
    timings = st.session_state.last_latency
    webhook_status = st.session_state.last_webhook_status
    webhook_latency = st.session_state.last_webhook_latency

    left_img, right_img = st.columns(2)
    with left_img:
        st.markdown("**Image originale**")
        st.image(load_image_from_bytes(image_bytes), use_column_width=True)
    with right_img:
        st.markdown("**Image annotee**")
        st.image(st.session_state.last_annotated, use_column_width=True)

    st.markdown("**Table detections**")
    if detections:
        st.dataframe(pd.DataFrame(detections))
    else:
        st.info("Aucun navire detecte.")

    st.markdown("**Pipeline**")
    webhook_step = "off"
    if webhook_status is not None:
        webhook_step = "ok" if 200 <= webhook_status < 300 else "warn"

    steps = [
        ("Load", "ok" if image_bytes else "off"),
        ("Preprocess", "ok" if timings.get("preprocess", 0) >= 0 else "off"),
        ("Inference", "ok" if timings.get("inference", 0) > 0 else "off"),
        ("Postprocess", "ok" if timings.get("postprocess", 0) >= 0 else "off"),
        ("Packet", "ok" if timings.get("packaging", 0) > 0 else "off"),
        ("Webhook", webhook_step),
        ("Done", "ok"),
    ]
    pipeline_bar(steps)
    timings_display = dict(timings)
    if webhook_latency is not None:
        timings_display["webhook"] = webhook_latency
    st.table(pd.DataFrame([timings_display]))

    st.markdown("**Event packet JSON**")
    packet_json = json.dumps(packet, indent=2)
    st.text_area("Event packet", value=packet_json, height=220)
    if st.button("Copy packet"):
        st.toast("Use Ctrl+C to copy from the text area.")

    st.markdown("**Webhook**")
    webhook_url = st.text_input("URL webhook", value="http://127.0.0.1:8000/webhook")
    if st.button("Send webhook"):
        status, body, latency = post_webhook(webhook_url, packet)
        st.session_state.last_webhook_status = status
        st.session_state.last_webhook_latency = latency
        st.session_state.events_log.append(
            {"event_id": packet.get("event_id"), "status": status, "latency_ms": latency}
        )
        if status >= 200 and status < 300:
            st.success(f"Sent. Status {status} in {latency:.1f} ms")
        else:
            st.session_state.errors_log.append({"event_id": packet.get("event_id"), "error": body})
            st.error(f"Webhook failed ({status}): {body}")
