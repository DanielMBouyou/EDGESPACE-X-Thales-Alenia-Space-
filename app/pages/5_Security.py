from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Sécurité", page_icon="🔒", layout="wide")
apply_theme()
init_state()

header("🔒 Sécurité & Audit", "Reproductibilité, intégrité, traçabilité complète.")

st.write("")

# ── Reproductibilité ─────────────────────────────────────────────────────────
st.markdown("### 🔁 Reproductibilité")
st.markdown(
    """
<div class="edge-card">
  <div style="color:#4b4f6b;font-size:14px;line-height:1.8;">
    <b>Mêmes entrées → mêmes sorties.</b> Garanti par :
    <ul>
      <li>✅ <b>Modèle versionné</b> — hash SHA-256 du fichier ONNX / PT</li>
      <li>✅ <b>Config figée</b> — seuil confiance, taille entrée, NMS fixés</li>
      <li>✅ <b>Hash partout</b> — entrée, modèle, packet</li>
      <li>✅ <b>NMS déterministe</b> — même algorithme, même ordre</li>
      <li>✅ <b>Pas de random</b> — inférence sans augmentation</li>
    </ul>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ── Chaîne d'intégrité ───────────────────────────────────────────────────────
st.markdown("### 🔗 Chaîne d'intégrité")

st.code(
    """
 ┌────────────────────┐
 │  📷 Image entrée   │
 │  SHA-256 → input_hash
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │  🧠 Modèle ONNX    │
 │  SHA-256 → model_hash
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │  📋 Event Packet   │
 │  SHA-256 → packet_hash
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │  🔑 Signature      │
 │  HMAC-SHA256(secret, packet_hash)
 │  → integrity.signature
 └────────────────────┘
""",
    language="text",
)

st.markdown("""
**Vérification côté récepteur :**
1. Recalculer `packet_hash` = SHA-256(packet sans integrity)
2. Vérifier `signature` = HMAC-SHA256(shared_secret, packet_hash)
3. Si match → packet authentique et non altéré
""")

st.divider()

# ── Robustesse opérationnelle ─────────────────────────────────────────────────
st.markdown("### 🛡️ Robustesse opérationnelle")

st.table(pd.DataFrame({
    "Scénario": [
        "Pas de GPU disponible",
        "Image corrompue / invalide",
        "Batch de N images",
        "Modèle manquant",
        "Webhook timeout",
        "Résultat vide (0 détections)",
    ],
    "Comportement": [
        "Fallback automatique CPU (ONNX Runtime)",
        "Rejet + log d'erreur + skip",
        "Traitement séquentiel, packet par image",
        "Erreur explicite, pas de crash",
        "3 retries avec backoff, log échec",
        "Event packet généré quand même (detections: [])",
    ],
    "Status": ["✅", "✅", "✅", "✅", "✅", "✅"],
}))

st.divider()

# ── Audit Trail ───────────────────────────────────────────────────────────────
st.markdown("### 📝 Audit Trail")

st.markdown("""
Chaque event packet contient sa propre traçabilité :

```json
{
  "input": {
    "input_hash": "sha256:abc123...",
    "image_size": [640, 640]
  },
  "model": {
    "model_name": "yolo11s-fire",
    "model_version": "sha256:def456...",
    "runtime": "onnx-fp16"
  },
  "integrity": {
    "packet_hash": "sha256:789abc...",
    "signature": "hmac-sha256:...",
    "model_hash": "sha256:def456..."
  }
}
```

**Logs exportables** → voir la page Logs.
""")

st.divider()

# ── Séparation Compute / Transport ────────────────────────────────────────────
st.markdown("### 📦 Séparation Compute vs Transport")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
<div class="edge-card" style="border-top:3px solid #e85d04;">
  <b>🧮 Compute (identique sol / orbite)</b>
  <ul style="color:#4b4f6b;margin-top:8px;">
    <li>Chargement image</li>
    <li>Pré-traitement (resize 640)</li>
    <li>Inférence ONNX</li>
    <li>NMS + filtrage</li>
    <li>Packaging event packet</li>
    <li>Signature HMAC</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
<div class="edge-card" style="border-top:3px solid #3b82f6;">
  <b>📡 Transport (seul élément différent)</b>
  <ul style="color:#4b4f6b;margin-top:8px;">
    <li><b>Sol (PoC) :</b> HTTP POST webhook</li>
    <li><b>Orbite :</b> Lien S/X-band → station sol → API</li>
    <li>Même payload JSON dans les deux cas</li>
    <li>Simulateur de downlink intégré au PoC</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
