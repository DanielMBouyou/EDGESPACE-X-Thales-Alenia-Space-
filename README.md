# 🛰️🔥 EDGE SPACE — Satellite Wildfire Detection

> **Détection rapide des feux de forêt à partir d'images satellites et d'IA embarquée.**
> On ne downlink pas des images — on downlink des **alertes vérifiables**.

**Projet startup — Incubateur Thales**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://edgespace.streamlit.app)

---

## 🎯 Concept

EDGE SPACE embarque un modèle **YOLO11s** directement sur le satellite. Au lieu de télécharger des images brutes (50–500 MB), le satellite transmet des **event packets signés** (~1.2 kB) contenant uniquement les détections, métadonnées et preuves cryptographiques.

| | Approche classique | EDGE SPACE |
|---|---|---|
| **Donnée transmise** | Image brute 50–500 MB | Event packet ~1.2 kB |
| **Temps downlink** | 13–130 min (S-band) | < 1 sec |
| **Latence alerte** | Heures | **< 90 sec** |
| **Réduction volume** | — | **99.99 %** |

---

## 📊 Performance du modèle

| Métrique | Valeur |
|---|---|
| Modèle | YOLO11s (9.4M params, 21.5 GFLOPs) |
| Dataset | [Satellite Inferno](https://universe.roboflow.com/) — 21 087 train / 2 009 val / 1 005 test |
| Classe | `fire` (1 classe) |
| Epochs | 27 |
| **mAP@50** | **52.0 %** |
| **mAP@50-95** | **27.5 %** |
| Precision | 60.5 % |
| Recall | 48.1 % |
| Runtime | PyTorch FP32 / ONNX FP32 |
| GPU entraînement | NVIDIA RTX 4050 Laptop (6 GB VRAM) |

---

## 📦 Event Packet

C'est **exactement** ce qui est transmis du satellite au sol — pas l'image.

```json
{
  "event_id": "c9d0a3b1-...",
  "event_type": "wildfire",
  "timestamp_utc": "2026-02-09T14:30:00Z",
  "sat_id": "EDGESPACE-SAT-01",
  "geolocation": { "lat": 36.778, "lon": -119.418, "geohash": "9q8yyk8yuv" },
  "detections": [
    { "bbox_px": [132, 88, 298, 236], "confidence": 0.94, "class": "fire" }
  ],
  "evidence": { "thumbnail_b64": "...", "thumbnail_hash": "sha256:..." },
  "integrity": {
    "packet_hash": "sha256:...",
    "signature": "hmac-sha256:...",
    "model_hash": "sha256:..."
  }
}
```

**~1.2 kB** vs ~50 MB image brute → **×41 000 plus compact**.

---

## 🏗️ Architecture

```
📷 Image satellite (640×640)
     │
     ▼
┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐
│ Ingestion│─▶│Pré-process│─▶│Inférence │─▶│Post-NMS │─▶│ Packet │
│ load/tile│  │resize/norm│  │ YOLO11s  │  │filtrage │  │ signer │
└──────────┘  └───────────┘  │ ONNX/PT  │  └─────────┘  └───┬────┘
                             └──────────┘                    │
                                                    ┌───────┤
                                                    ▼       ▼
                                             ┌──────────┐ ┌─────────┐
                                             │ Evidence │ │ Webhook │
                                             │thumb+hash│ │POST API │
                                             └──────────┘ └─────────┘
```

**3 blocs logiciels :**

1. **UI Streamlit** — vitrine + bac à sable de test *(démo uniquement)*
2. **Inference Engine** (`src/infer/`) — runtime ONNX/PyTorch, déterministe *(sol + orbite)*
3. **Packetizer + Signer** — event packet JSON, SHA-256 + HMAC *(sol + orbite)*

---

## 🚀 Streamlit PoC — 7 pages

| Page | Description |
|---|---|
| 🏠 **Home** | Hero, KPIs clés, comparatif image vs packet |
| 🔬 **Try it** | Upload → pipeline 5 étapes → event packet → webhook |
| 📊 **KPIs** | Métriques modèle, taille payload, budget latence |
| 🛰️ **Satellite Proof** | Profils LP/HP, specs D-Orbit ION, latence P50/P95 |
| 🏗️ **Architecture** | 3 blocs, pipeline, Dockerfile, continuous improvement |
| 🔒 **Security** | Chaîne d'intégrité SHA-256→HMAC, reproductibilité |
| 📡 **API** | Schéma JSON, webhook test, mock server, cURL |
| 📜 **Logs** | Journal events/erreurs, export JSON, audit |

---

## 🛠️ Installation

```bash
git clone https://github.com/your-org/edgespace.git
cd edgespace

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### GPU (entraînement / inférence rapide)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install ultralytics
```

---

## ▶️ Utilisation

### Lancer le PoC Streamlit

```bash
streamlit run Home.py
```

### Entraînement

```bash
python src/train/train_optimized.py
```

### Reprendre un entraînement interrompu

```bash
python scripts/resume_training.py
```

### Export ONNX

```bash
python -c "from ultralytics import YOLO; YOLO('models/weights/best.pt').export(format='onnx', simplify=True)"
```

### Serveur mock webhook

```bash
python scripts/mock_webhook.py
# Écoute sur http://127.0.0.1:8000/webhook
```

---

## 📁 Structure du projet

```
├── Home.py                   # Point d'entrée Streamlit
├── streamlit_app.py          # Alias Cloud
├── requirements.txt
├── app/
│   ├── Home.py               # Page d'accueil (hero + KPIs)
│   ├── pages/                # 7 pages Streamlit
│   ├── ui.py                 # Composants UI (theme, cards)
│   ├── state.py              # Session state
│   └── utils.py              # ROOT path
├── src/
│   ├── infer/                # Inference engine
│   │   ├── predict_pt.py     # Inférence PyTorch
│   │   ├── predict_onnx.py   # Inférence ONNX
│   │   ├── event_packet.py   # Génération event packet
│   │   ├── webhook.py        # Client webhook
│   │   └── runtime.py        # Chargement modèles
│   ├── train/                # Scripts d'entraînement
│   ├── convert/              # Conversion datasets
│   └── utils/                # Hashing, timing, NMS, image
├── models/weights/           # best.pt / best.onnx (gitignored)
├── datasets/                 # Données d'entraînement (gitignored)
├── pages/                    # Proxy → app/pages/ (multi-page Streamlit)
├── scripts/                  # Utilitaires (download, resume, mock)
└── runs/                     # Résultats training
    └── summary.json          # Métriques finales (versionné)
```

---

## 🔒 Sécurité & Intégrité

```
📷 Image → SHA-256 → input_hash
🧠 Modèle → SHA-256 → model_hash
📋 Packet → SHA-256 → packet_hash → HMAC-SHA256(secret) → signature
```

- **Reproductibilité** : mêmes entrées → mêmes sorties (NMS déterministe, pas de random)
- **Traçabilité** : chaque packet contient hash entrée + hash modèle + signature
- **Vérification** : HMAC-SHA256 avec shared secret

---

## 🛰️ Compatibilité orbitale

| Profil | Compute | Puissance | Inférence/tile | Référence |
|---|---|---|---|---|
| **LP** (Low Power) | Intel Myriad X | 1–2 W | 500–1000 ms | Φ-Sat-2 |
| **HP** (High Perf) | AMD64 + GPU | 15–25 W | 30–80 ms | Moog iX5 |

**Plateforme cible** : D-Orbit ION Satellite Carrier (hosted payload)
- Télécom S-band ~500 kbps (suffisant pour event packets)
- Télécom X-band >50 Mbps (backup evidence)
- Mise à jour modèle en orbite ✅

---

## 🌐 Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `EDGE_SPACE_HMAC_SECRET` | Secret HMAC pour signature packets | `demo-secret` |

Créer un fichier `.env` à la racine (gitignored).

---

## 📜 Licence

Projet interne — Incubateur Thales.

---

*EDGE SPACE — Détection rapide des feux de forêt à partir d'images satellites et d'IA embarquée · Incubateur Thales*
