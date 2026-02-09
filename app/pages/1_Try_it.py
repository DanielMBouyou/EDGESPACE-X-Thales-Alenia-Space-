from __future__ import annotations

import base64
import io
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, List

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

st.set_page_config(page_title="EDGE SPACE — Try it", page_icon="🔥", layout="wide")
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
    "🔬 Try it — Bac à sable",
    "Upload une image satellite, observe le pipeline complet, récupère l'event packet.",
)

st.write("")

# ── Configuration ─────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])
with left:
    mode = st.radio(
        "Mode runtime",
        ["Sol (PyTorch GPU/CPU)", "Orbite (ONNX quantifié)"],
        horizontal=True,
        help="Sol = modèle PyTorch complet. Orbite = modèle ONNX optimisé comme en vol.",
    )
    conf_threshold = st.slider("Seuil de confiance", 0.1, 0.95, 0.25, 0.05)

with right:
    st.markdown("**🛰️ Simulateur downlink**")
    orbital_profile = st.selectbox(
        "Profil orbital", ["LP — Low Power (Φ-Sat)", "HP — High Perf (Moog iX5)"]
    )
    transmission = st.selectbox(
        "Liaison", ["Direct Station Sol", "Relais GEO (TDRS / SpaceDataHighway)"]
    )
    downlink_delay = st.number_input("Délai downlink (sec)", 0.0, 60.0, 3.5, 0.5)
    queue_delay = st.number_input("Délai queue (sec)", 0.0, 30.0, 1.2, 0.5)

st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("### 📤 Upload")
upload_tab, sample_tab = st.tabs(["📁 Drag & Drop", "📎 Échantillons démo"])

with upload_tab:
    col_single, col_batch = st.columns(2)
    with col_single:
        uploaded = st.file_uploader(
            "Image unique (jpg / png / tif)",
            type=["jpg", "jpeg", "png", "tif", "tiff"],
            key="single_upload",
        )
    with col_batch:
        uploaded_zip = st.file_uploader(
            "Batch (ZIP) — simule un passage satellite",
            type=["zip"],
            key="batch_upload",
        )

with sample_tab:
    sample_dir = ROOT / "datasets" / "demo_samples"
    samples = (
        sorted(
            p
            for p in sample_dir.glob("*.*")
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
        )
        if sample_dir.exists()
        else []
    )
    if samples:
        thumb_cols = st.columns(min(6, len(samples)))
        for idx, p in enumerate(samples[:6]):
            with thumb_cols[idx % len(thumb_cols)]:
                st.image(p.read_bytes(), caption=p.name, width=100)
        sample_choice = st.selectbox("Choisir un échantillon", [p.name for p in samples])
        use_sample = st.button("Utiliser cet échantillon")
    else:
        st.info("Aucun échantillon dans `datasets/demo_samples/`. Ajoutez des images satellite.")
        sample_choice = None
        use_sample = False

# Collect images
images_to_process: List[tuple] = []
if uploaded is not None:
    images_to_process.append((uploaded.name, uploaded.getvalue()))
elif uploaded_zip is not None:
    with zipfile.ZipFile(io.BytesIO(uploaded_zip.getvalue())) as zf:
        for name in zf.namelist():
            if name.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                images_to_process.append((name, zf.read(name)))
    st.success(f"📦 Batch : {len(images_to_process)} images extraites du ZIP")
elif use_sample and sample_choice:
    sp = sample_dir / sample_choice
    images_to_process.append((sample_choice, sp.read_bytes()))

st.divider()

# ── Run pipeline ──────────────────────────────────────────────────────────────
run = st.button("🚀 Lancer la détection", type="primary", use_container_width=True)

if run and not images_to_process:
    st.warning("⚠️ Upload une image ou choisis un échantillon d'abord.")

if run and images_to_process:
    all_packets: List[dict] = []
    all_detections_list: List[list] = []
    progress = st.progress(0, text="Initialisation…")
    total = len(images_to_process)

    for img_idx, (img_name, image_bytes) in enumerate(images_to_process):
        st.markdown(f"---\n**Image {img_idx + 1}/{total}** : `{img_name}`")
        image = load_image_from_bytes(image_bytes)
        input_hash = sha256_bytes(image_bytes)
        timings: Dict[str, float] = {}

        # STEP 1 — Ingestion
        progress.progress(
            (img_idx * 5 + 1) / (total * 5),
            text=f"[{img_idx+1}/{total}] 1/5 — Ingestion…",
        )
        with timing(timings, "ingestion"):
            orig_w, orig_h = image.size
        st.caption(f"📐 {orig_w}×{orig_h} px | Hash: `{input_hash[:16]}…`")

        # STEP 2 — Pré-traitement
        progress.progress(
            (img_idx * 5 + 2) / (total * 5),
            text=f"[{img_idx+1}/{total}] 2/5 — Pré-traitement…",
        )
        with timing(timings, "preprocess_step"):
            pass  # resize handled inside predict

        # STEP 3 — Inférence
        progress.progress(
            (img_idx * 5 + 3) / (total * 5),
            text=f"[{img_idx+1}/{total}] 3/5 — Inférence IA…",
        )
        if mode.startswith("Sol"):
            weights = ROOT / "models" / "weights" / "best.pt"
            if not weights.exists():
                st.error("❌ Modèle manquant : `models/weights/best.pt`. Entraîne d'abord.")
                st.stop()
            model = get_pt_model(str(weights))
            detections, det_timings = predict_pt(
                image, model=model, conf_thres=conf_threshold
            )
            runtime_name = "pytorch-fp32"
            model_hash = sha256_file(weights)
        else:
            onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
            onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
            onnx_path = onnx_int8 if onnx_int8.exists() else onnx_fp32
            if not onnx_path.exists():
                st.error("❌ Modèle ONNX manquant. Exporte avec `src/infer/export_onnx.py`.")
                st.stop()
            session = get_onnx_session(str(onnx_path))
            input_name = session.get_inputs()[0].name
            detections, det_timings = predict_onnx(
                image, session=session, input_name=input_name, conf_thres=conf_threshold
            )
            runtime_name = "onnx-int8" if "int8" in onnx_path.name else "onnx-fp32"
            model_hash = sha256_file(onnx_path)
        timings.update(det_timings)

        # STEP 4 — Post-traitement
        progress.progress(
            (img_idx * 5 + 4) / (total * 5),
            text=f"[{img_idx+1}/{total}] 4/5 — Post-traitement…",
        )
        with timing(timings, "postprocess_extra"):
            n_det = len(detections)

        # STEP 5 — Event Packet
        progress.progress(
            (img_idx * 5 + 5) / (total * 5),
            text=f"[{img_idx+1}/{total}] 5/5 — Event Packet…",
        )
        # Evidence thumbnail
        thumb = image.copy()
        thumb.thumbnail((128, 128))
        buf = io.BytesIO()
        thumb.save(buf, format="JPEG", quality=60)
        thumb_bytes = buf.getvalue()
        thumb_b64 = base64.b64encode(thumb_bytes).decode()
        thumb_hash = sha256_bytes(thumb_bytes)

        with timing(timings, "packaging"):
            packet = make_event_packet(
                detections,
                {
                    "input_hash": input_hash,
                    "image_size": [orig_w, orig_h],
                    "model_name": "yolo11s-fire",
                    "model_version": model_hash,
                    "runtime": runtime_name,
                    "event_type": "wildfire",
                    "sensor_mode": "Optical/IR",
                    "sat_id": "EDGESPACE-SIM-01",
                    "thumbnail_b64": thumb_b64,
                    "thumbnail_hash": f"sha256:{thumb_hash[:16]}",
                    "latency_ms": {},
                },
                secret=os.environ.get("EDGE_SPACE_HMAC_SECRET", "demo-secret"),
            )

        timings["total"] = sum(v for k, v in timings.items() if k != "total")
        timings["downlink_sim"] = (downlink_delay + queue_delay) * 1000
        timings["end_to_end_est"] = timings["total"] + timings["downlink_sim"]
        packet["latency_ms"] = {k: round(v, 2) for k, v in timings.items()}

        all_packets.append(packet)
        all_detections_list.append(detections)

        # ── Display results ───────────────────────────────────────────────────
        annotated = draw_bboxes(
            image,
            [d["bbox_px"] for d in detections],
            [f"fire {d['confidence']:.0%}" for d in detections],
            color=(255, 80, 0),
            width=3,
        )

        col_orig, col_annot = st.columns(2)
        with col_orig:
            st.image(image, caption="Image originale", use_container_width=True)
        with col_annot:
            st.image(annotated, caption=f"Détections : {n_det} feu(x)", use_container_width=True)

        pipeline_bar([
            ("1. Ingestion", "ok"),
            ("2. Pré-traitement", "ok"),
            ("3. Inférence", "ok"),
            ("4. Post-traitement", "ok"),
            ("5. Event Packet", "ok"),
        ])

        st.markdown("**⏱️ Chronométrage (ms)**")
        st.dataframe(
            pd.DataFrame([{k: f"{v:.1f}" for k, v in timings.items()}]),
            use_container_width=True,
        )

        if detections:
            st.markdown(f"**🔥 {n_det} détection(s)**")
            st.dataframe(pd.DataFrame(detections), use_container_width=True)
        else:
            st.info("Aucun feu détecté sur cette image.")

    progress.progress(1.0, text="✅ Terminé !")

    # Store
    st.session_state.last_packet = all_packets[-1] if all_packets else None
    st.session_state.last_detections = all_detections_list[-1] if all_detections_list else []
    st.session_state.last_latency = timings
    st.session_state.batch_packets = all_packets

    # ── Event Packet JSON ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Event Packet JSON")
    packet_json = json.dumps(all_packets[-1], indent=2)
    st.code(packet_json, language="json")
    packet_size_kb = len(packet_json.encode()) / 1024
    st.metric("📦 Taille du packet", f"{packet_size_kb:.2f} kB")

    st.download_button(
        "⬇️ Télécharger Event Packet",
        data=packet_json,
        file_name=f"event_packet_{all_packets[-1]['event_id'][:8]}.json",
        mime="application/json",
    )
    if len(all_packets) > 1:
        all_json = json.dumps(all_packets, indent=2)
        st.download_button(
            f"⬇️ Télécharger tous les packets ({len(all_packets)})",
            data=all_json,
            file_name="event_packets_batch.json",
            mime="application/json",
        )

    # ── Audit Trail ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🔒 Audit Trail")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        st.text_input("Hash entrée (SHA-256)", value=input_hash, disabled=True)
    with ac2:
        st.text_input("Hash modèle", value=model_hash[:32] + "…", disabled=True)
    with ac3:
        st.text_input(
            "Hash packet",
            value=all_packets[-1]["integrity"]["packet_hash"][:32] + "…",
            disabled=True,
        )

    # ── Webhook ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📡 Webhook Test")
    webhook_url = st.text_input("URL webhook", value="http://127.0.0.1:8000/webhook")
    if st.button("📤 Envoyer le webhook"):
        with st.spinner("Envoi en cours…"):
            status, body, latency = post_webhook(webhook_url, all_packets[-1])
        st.session_state.last_webhook_status = status
        st.session_state.last_webhook_latency = latency
        st.session_state.events_log.append(
            {
                "event_id": all_packets[-1]["event_id"],
                "status": status,
                "latency_ms": round(latency, 1),
                "timestamp": all_packets[-1]["timestamp_utc"],
            }
        )
        if 200 <= status < 300:
            st.success(f"✅ Envoyé — HTTP {status} en {latency:.1f} ms")
        else:
            st.session_state.errors_log.append(
                {"event_id": all_packets[-1]["event_id"], "error": body[:200]}
            )
            st.error(f"❌ Échec — HTTP {status} : {body[:200]}")
        st.markdown("**Payload envoyé :**")
        st.code(json.dumps(all_packets[-1], indent=2)[:2000], language="json")
