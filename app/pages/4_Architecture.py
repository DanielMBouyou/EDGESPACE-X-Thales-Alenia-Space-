from __future__ import annotations

import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Architecture", page_icon="🏗️", layout="wide")
apply_theme()
init_state()

header("🏗️ Architecture", "3 blocs logiciels — du PoC à l'orbite, même code.")

st.write("")

# ── 3 blocs ───────────────────────────────────────────────────────────────────
st.markdown("### 🧱 3 blocs logiciels")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;border-top:4px solid #3b82f6;">
  <div style="font-weight:700;font-size:16px;margin-bottom:10px;">1️⃣ UI Streamlit</div>
  <div style="color:#4b4f6b;font-size:13px;">
    • Vitrine + bac à sable de test<br/>
    • Upload drag &amp; drop (single / batch ZIP)<br/>
    • Visualisation pipeline 5 étapes<br/>
    • Export JSON / Webhook<br/><br/>
    <span class="edge-pill">DEMO ONLY</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;border-top:4px solid #e85d04;">
  <div style="font-weight:700;font-size:16px;margin-bottom:10px;">2️⃣ Inference Engine</div>
  <div style="color:#4b4f6b;font-size:13px;">
    • Lib Python autonome (<code>src/infer/</code>)<br/>
    • Runtime ONNX ou PyTorch<br/>
    • Pré/post-traitement déterministe<br/>
    • NMS + filtrage confiance<br/><br/>
    <span class="edge-pill">SOL + ORBITE</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;border-top:4px solid #16a34a;">
  <div style="font-weight:700;font-size:16px;margin-bottom:10px;">3️⃣ Packetizer + Signer</div>
  <div style="color:#4b4f6b;font-size:13px;">
    • Génération event packet JSON<br/>
    • Hash SHA-256 (entrée, modèle, packet)<br/>
    • Signature HMAC-SHA256<br/>
    • Client webhook + idempotency key<br/><br/>
    <span class="edge-pill">SOL + ORBITE</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ── Pipeline ──────────────────────────────────────────────────────────────────
st.markdown("### 🔄 Pipeline complète")

st.code(
    """
╔════════════════════════════════════════════════════════════════════════════╗
║                        EDGE SPACE — Pipeline                             ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║   📷 Image Satellite (tile 640×640)                                      ║
║        │                                                                 ║
║        ▼                                                                 ║
║   ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐ ║
║   │ Ingestion│─▶│ Pré-process │─▶│Inférence │─▶│Post-NMS │─▶│ Packet │ ║
║   │ load/tile│  │ resize/norm │  │ YOLO11s  │  │ filtrage│  │ signer │ ║
║   └──────────┘  └─────────────┘  │ ONNX/PT  │  │ cluster │  └───┬────┘ ║
║                                  └──────────┘  └─────────┘      │      ║
║                                                     ┌───────────┤      ║
║                                                     ▼           ▼      ║
║                                              ┌──────────┐ ┌─────────┐  ║
║                                              │ Evidence │ │ Webhook │  ║
║                                              │thumb+hash│ │POST API │  ║
║                                              └──────────┘ └─────────┘  ║
╚════════════════════════════════════════════════════════════════════════════╝
""",
    language="text",
)

st.divider()

# ── Déploiement orbital ───────────────────────────────────────────────────────
st.markdown("### 🚀 Déploiement orbital")

st.markdown(
    """
<div class="edge-card">
  <div style="font-weight:700;font-size:16px;margin-bottom:12px;">Empaquetage conteneur</div>
  <div style="color:#4b4f6b;font-size:14px;">
    Le bloc <b>Inference Engine</b> + <b>Packetizer</b> est empaquetable en conteneur léger :
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.code(
    """
# Dockerfile orbital (exemple)
FROM python:3.12-slim

COPY src/infer/ /app/infer/
COPY src/utils/ /app/utils/
COPY models/weights/best.onnx /app/models/

RUN pip install onnxruntime numpy pillow

ENTRYPOINT ["python", "-m", "app.infer.runtime"]
""",
    language="dockerfile",
)

st.markdown("""
**Mêmes entrées / sorties :**
- **Entrée** : image satellite (tile 640×640)
- **Sortie** : event packet JSON signé (~1.2 kB)

**Ce qui change** : le transport (filesystem / API locale → lien S/X-band).

| Profil | Compute | Runtime | Modèle |
|---|---|---|---|
| LP (Low Power) | Myriad X / edge TPU | ONNX INT8 | best.int8.onnx |
| HP (High Perf) | AMD64 + GPU | ONNX FP16 | best.onnx |
| Sol (démo) | GPU desktop | PyTorch FP32 | best.pt |
""")

st.divider()

# ── Continuous improvement ────────────────────────────────────────────────────
st.markdown("### 🔄 Continuous Improvement en orbite")

st.markdown("""
Grâce au stockage embarqué (128 Gb+) et à la capacité de mise à jour logicielle :

1. **Upload** nouveau modèle ONNX via station sol
2. **Validation** on-board (test sur images de référence)
3. **Switch** vers le nouveau modèle (rollback possible)
4. **Télémétrie** : métriques de performance remontées via event packets

➡️ Le modèle s'améliore continuellement sans changer le hardware.
""")
