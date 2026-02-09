from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header, metric_card
from app.utils import ROOT
from src.infer.runtime import model_size_mb

st.set_page_config(page_title="EDGE SPACE — Satellite Proof", page_icon="🛰️", layout="wide")
apply_theme()
init_state()

header("🛰️ On-Orbit Equivalence", "Pourquoi le même code peut tourner en orbite — preuves et specs.")

st.write("")

# ── Ce qui change / ne change pas ────────────────────────────────────────────
st.markdown("### 🔄 Ce qui change en orbite (et ce qui ne change pas)")

col_same, col_diff = st.columns(2)
with col_same:
    st.markdown(
        """
<div class="edge-card" style="border-left:4px solid #16a34a;">
  <b>✅ Ne change PAS</b>
  <ul style="margin-top:8px;color:#4b4f6b;">
    <li>Code d'inférence (même binaire / conteneur)</li>
    <li>Format du modèle ONNX</li>
    <li>Format de l'event packet (JSON signé)</li>
    <li>Pipeline : ingest → preprocess → infer → packet</li>
    <li>Algorithme NMS déterministe</li>
    <li>Hash &amp; signature HMAC</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with col_diff:
    st.markdown(
        """
<div class="edge-card" style="border-left:4px solid #f59e0b;">
  <b>⚠️ Change</b>
  <ul style="margin-top:8px;color:#4b4f6b;">
    <li>Contraintes puissance (1-25 W vs 300 W)</li>
    <li>Contraintes mémoire (0.5-2 GB vs 16+ GB)</li>
    <li>Bande passante downlink (kbps – Mbps)</li>
    <li>Radiations / température</li>
    <li>Fenêtres de contact (min / orbite)</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ── LP / HP Switch ────────────────────────────────────────────────────────────
st.markdown("### ⚡ Profils Compute Orbital")

orbital_mode = st.radio(
    "Profil",
    ["🔋 Mode Orbital-LP (Low Power)", "🖥️ Mode Orbital-HP (High Performance)"],
    horizontal=True,
)

if orbital_mode.startswith("🔋"):
    st.markdown(
        """
<div class="edge-card">
  <div style="font-weight:700;font-size:18px;margin-bottom:12px;">
    🔋 Profil LP — Ultra Low-Power AI Accelerator
  </div>
  <div style="color:#4b4f6b;font-size:14px;">
    <b>Référence :</b> Φ-Sat-2 / Intel Myriad X — démontré en vol pour cloud detection CNN.<br/>
    <b>Message business :</b> <i>"On sait faire de l'IA utile avec quelques watts."</i>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("⚡ Puissance", "1 – 2 W", "Accélérateur IA économe")
    with c2:
        metric_card("🧠 RAM", "512 MB", "DDR / on-chip")
    with c3:
        metric_card("⏱️ Inférence", "500 – 1000 ms", "Par tile 640×640")
    with c4:
        metric_card("📦 Packet", "~1.2 kB", "Même format")

    st.markdown("**Contraintes LP :**")
    st.table(pd.DataFrame({
        "Paramètre": ["Compute", "RAM", "Stockage", "Puissance", "Inférence / tile", "Modèle max", "OS"],
        "Valeur": [
            "Intel Myriad X / edge TPU",
            "256 – 512 MB",
            "8 – 32 GB eMMC",
            "1 – 2 W",
            "500 – 1000 ms",
            "~20 MB ONNX INT8",
            "Linux embedded / RTOS",
        ],
    }))

else:
    st.markdown(
        """
<div class="edge-card">
  <div style="font-weight:700;font-size:18px;margin-bottom:12px;">
    🖥️ Profil HP — Rugged x86 + GPU (classe avionique)
  </div>
  <div style="color:#4b4f6b;font-size:14px;">
    <b>Référence :</b> Moog Deep Delphi iX5 — AMD64, Linux, GPU compute ~77 GFLOP.<br/>
    <b>Message business :</b> <i>"On peut embarquer un vrai compute edge si le payload le justifie."</i>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("⚡ Puissance", "15 – 25 W", "GPU + CPU")
    with c2:
        metric_card("🧠 RAM", "2 GB ECC", "DDR3 ECC + 0.5 GB FPGA")
    with c3:
        metric_card("⏱️ Inférence", "30 – 80 ms", "Par tile 640×640")
    with c4:
        metric_card("📦 Packet", "~1.2 kB", "Même format")

    st.markdown("**Contraintes HP :**")
    st.table(pd.DataFrame({
        "Paramètre": [
            "Compute", "RAM", "Stockage", "GPU", "Puissance",
            "Inférence / tile", "Modèle max", "OS",
        ],
        "Valeur": [
            "AMD64 (x86)",
            "2 GB DDR3 ECC + 0.5 GB FPGA",
            "eMMC + jusqu'à 768 GB SSD M.2",
            "~77 GFLOP",
            "15 – 25 W",
            "30 – 80 ms",
            "~50 MB ONNX FP16",
            "Linux",
        ],
    }))

st.divider()

# ── Compatibilité modèle ─────────────────────────────────────────────────────
st.markdown("### 📐 Compatibilité du modèle actuel")

onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
pt_path = ROOT / "models" / "weights" / "best.pt"

compat_rows = []
for label, path, max_lp, max_hp in [
    ("best.pt", pt_path, 20, 50),
    ("best.onnx", onnx_fp32, 20, 50),
    ("best.int8.onnx", onnx_int8, 20, 50),
]:
    if path.exists():
        size = model_size_mb(path)
        compat_rows.append({
            "Modèle": label,
            "Taille (MB)": f"{size:.1f}",
            "LP compatible": "✅" if size <= max_lp else "❌",
            "HP compatible": "✅" if size <= max_hp else "⚠️",
        })

if compat_rows:
    st.table(pd.DataFrame(compat_rows))
else:
    st.info("Aucun modèle disponible. L'entraînement est peut-être en cours…")

st.divider()

# ── Plateforme satellite ──────────────────────────────────────────────────────
st.markdown("### 🚀 Plateforme satellite (hosted payload)")

st.markdown(
    """
<div class="edge-card">
  <div style="font-weight:700;font-size:16px;margin-bottom:10px;">
    Intégration type : D-Orbit ION Satellite Carrier (hosted payload)
  </div>
  <div style="color:#4b4f6b;font-size:14px;">
    Vous ne construisez pas une constellation : vous embarquez votre compute + votre app
    sur une plateforme existante.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.table(pd.DataFrame({
    "Paramètre": [
        "Télécom S-band (omni)",
        "Télécom X-band (directionnel)",
        "Interfaces data",
        "Stockage OBDH",
        "Mise à jour en orbite",
        "Orbite type",
    ],
    "Valeur": [
        "≈ 500 kbps — suffisant pour event packets",
        "> 50 Mbps — backup pour evidence / thumbnails",
        "Ethernet, USB/UART, SPI, I2C",
        "Jusqu'à 128 Gb + SSD M.2",
        "✅ Upload nouvelle version modèle (continuous improvement)",
        "LEO 500-600 km, SSO",
    ],
}))

st.divider()

# ── Latence : justification quasi temps réel ──────────────────────────────────
st.markdown("### ⏱️ Justification « quasi temps réel »")

st.code(
    """
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────┐
│  🛰️ On-board    │ ──▶ │  📡 Downlink  │ ──▶ │  🌍 Ground   │ ──▶ │ 🔔 API  │
│  Inférence      │     │  S/X-band    │     │  Station     │     │ Webhook │
│  T_infer        │     │  T_downlink  │     │  T_buffer    │     │ T_api   │
│  50 ms – 1 s    │     │  < 1 s       │     │  variable    │     │ < 1 s   │
└─────────────────┘     └──────────────┘     └──────────────┘     └─────────┘
""",
    language="text",
)

st.markdown("""
**Relais GEO pour réduire T_buffer :**
- **TDRS (NASA)** : couverture LEO ~15 % → > 95 % via relais GEO
- **SpaceDataHighway (ESA / Airbus)** : relais optique LEO → GEO, latence < 1 s
- **Relais commerciaux US** : "real-time tasking & data dissemination"
""")

st.table(pd.DataFrame({
    "Scénario": [
        "Direct station sol",
        "Relais GEO",
    ],
    "T_infer": ["50 ms", "50 ms"],
    "T_buffer": ["~5 min (pire cas)", "< 10 s"],
    "T_downlink": ["< 1 s", "< 1 s"],
    "T_api": ["< 1 s", "< 1 s"],
    "Total P50": ["~5 min", "< 15 sec"],
    "Total P95": ["~15 min", "< 60 sec"],
}))

st.caption("Le goulot est **T_buffer** (attente fenêtre de contact) — pas l'IA.")

st.divider()

# ── Key message ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="edge-card" style="text-align:center;padding:24px;border-left:4px solid #16a34a;">
  <div style="font-size:18px;font-weight:700;">
    🎯 Le PoC génère <u>exactement</u> le même event packet que l'orbite.<br/>
    Seul le transport change (simulateur de downlink ↔ lien S/X-band réel).
  </div>
</div>
""",
    unsafe_allow_html=True,
)
