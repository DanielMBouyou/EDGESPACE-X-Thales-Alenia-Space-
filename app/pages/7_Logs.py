from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Logs", page_icon="📜", layout="wide")
apply_theme()
init_state()

header("📜 Logs", "Journal des événements, erreurs et audit exportable.")

st.write("")

# ── Events log ────────────────────────────────────────────────────────────────
st.markdown("### 📬 Events envoyés")

if st.session_state.events_log:
    df_events = pd.DataFrame(st.session_state.events_log)
    st.dataframe(df_events, use_container_width=True)
    st.download_button(
        "⬇️ Exporter events (JSON)",
        data=json.dumps(st.session_state.events_log, indent=2),
        file_name="events_log.json",
        mime="application/json",
    )
else:
    st.info("Aucun event envoyé. Utilise « Try it » → « Send webhook ».")

st.divider()

# ── Errors log ────────────────────────────────────────────────────────────────
st.markdown("### ❌ Erreurs webhook")

if st.session_state.errors_log:
    df_errors = pd.DataFrame(st.session_state.errors_log)
    st.dataframe(df_errors, use_container_width=True)
    st.download_button(
        "⬇️ Exporter erreurs (JSON)",
        data=json.dumps(st.session_state.errors_log, indent=2),
        file_name="errors_log.json",
        mime="application/json",
    )
else:
    st.info("Aucune erreur enregistrée. ✅")

st.divider()

# ── Batch results ─────────────────────────────────────────────────────────────
st.markdown("### 📦 Derniers packets générés")

if st.session_state.batch_packets:
    n = len(st.session_state.batch_packets)
    st.caption(f"{n} packet(s) en mémoire")
    for i, pkt in enumerate(st.session_state.batch_packets):
        with st.expander(f"Packet {i + 1} — {pkt.get('event_id', '?')[:8]}…"):
            st.code(json.dumps(pkt, indent=2), language="json")
    st.download_button(
        f"⬇️ Exporter tous les packets ({n})",
        data=json.dumps(st.session_state.batch_packets, indent=2),
        file_name="all_packets.json",
        mime="application/json",
    )
else:
    st.info("Aucun packet en mémoire. Lance une détection d'abord.")

st.divider()

# ── Robustesse ────────────────────────────────────────────────────────────────
st.markdown("### 🛡️ Robustesse opérationnelle")

st.markdown("""
| Vérification | Status |
|---|---|
| Fallback CPU si pas de GPU | ✅ ONNX Runtime CPU |
| Gestion batch (N images) | ✅ Traitement séquentiel |
| Rejet inputs invalides | ✅ Try / except + log |
| Logs exportables | ✅ JSON download |
| Mode dégradé (modèle absent) | ✅ Erreur explicite |
""")

# ── Clear logs ────────────────────────────────────────────────────────────────
st.divider()
if st.button("🗑️ Effacer tous les logs"):
    st.session_state.events_log = []
    st.session_state.errors_log = []
    st.session_state.batch_packets = []
    st.rerun()
