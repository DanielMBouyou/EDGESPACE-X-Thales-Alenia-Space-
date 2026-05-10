# EDGE SPACE — Satellite Wildfire Detection

> Wildfire detection from satellite imagery using on-board AI. The satellite does not downlink images — it downlinks verifiable, signed event packets.

Project developed within the Thales Incubator.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://edgespace.streamlit.app)

---

## Concept

EDGE SPACE runs a YOLO11s detector directly on the satellite. Instead of transmitting raw images (50–500 MB), the satellite emits compact signed event packets (~1.2 kB) containing the detections, metadata and cryptographic evidence required to verify them on the ground.

| | Classic approach | EDGE SPACE |
|---|---|---|
| Transmitted data | Raw image, 50–500 MB | Event packet, ~1.2 kB |
| Downlink time | 13–130 min (S-band) | < 1 sec |
| Alert latency | Hours | < 90 sec |
| Volume reduction | — | 99.99 % |

---

## Model performance

| Metric | Value |
|---|---|
| Model | YOLO11s (9.4M parameters, 21.5 GFLOPs) |
| Dataset | [Satellite Inferno](https://universe.roboflow.com/) — 21,087 train / 2,009 val / 1,005 test |
| Class | `fire` (single class) |
| Epochs | 27 |
| mAP@50 | 52.0 % |
| mAP@50-95 | 27.5 % |
| Precision | 60.5 % |
| Recall | 48.1 % |
| Runtime | PyTorch FP32 / ONNX FP32 |
| Training GPU | NVIDIA RTX 4050 Laptop (6 GB VRAM) |

---

## Event packet

This is exactly what is transmitted from the satellite to the ground — not the image.

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

~1.2 kB versus ~50 MB for a raw image — a 41,000× reduction.

---

## Architecture

```
Satellite tile (640x640)
    |
    v
+----------+   +-------------+   +----------+   +---------+   +--------+
| Ingest   |-->| Pre-process |-->| Inference|-->| Post-NMS|-->| Packet |
| load     |   | resize/norm |   | YOLO11s  |   | filter  |   | signer |
+----------+   +-------------+   | ONNX/PT  |   +---------+   +---+----+
                                 +----------+                     |
                                                       +----------+
                                                       |          |
                                                       v          v
                                                +----------+ +---------+
                                                | Evidence | | Webhook |
                                                |thumb+hash| |POST API |
                                                +----------+ +---------+
```

Three software blocks:

1. **UI Streamlit** — showcase and test sandbox (demo only).
2. **Inference engine** (`src/infer/`) — deterministic ONNX/PyTorch runtime (ground and orbit).
3. **Packetizer + signer** — JSON event packet, SHA-256 + HMAC (ground and orbit).

---

## Streamlit PoC — seven pages

| Page | Description |
|---|---|
| Home | Hero, key KPIs, image vs packet comparison |
| Try it | Upload → five-step pipeline → event packet → webhook |
| KPIs | Model metrics, payload size, latency budget |
| Satellite proof | LP/HP profiles, D-Orbit ION specifications, P50/P95 latency |
| Architecture | Three blocks, pipeline, Dockerfile, continuous improvement |
| Security | SHA-256 → HMAC integrity chain, reproducibility |
| API | JSON schema, webhook test, mock server, cURL |
| Logs | Events / errors journal, JSON export, audit |

---

## Installation

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

### GPU (training and faster inference)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install ultralytics
```

---

## Usage

### Run the Streamlit PoC

```bash
streamlit run Home.py
```

### Training

```bash
python src/train/train_optimized.py
```

### Resume an interrupted training run

```bash
python scripts/resume_training.py
```

### ONNX export

```bash
python -c "from ultralytics import YOLO; YOLO('models/weights/best.pt').export(format='onnx', simplify=True)"
```

### Mock webhook server

```bash
python scripts/mock_webhook.py
# Listening on http://127.0.0.1:8000/webhook
```

---

## Project structure

```
.
├── Home.py                   # Streamlit entry point
├── streamlit_app.py          # Cloud alias
├── requirements.txt
├── packages.txt              # apt packages for Streamlit Cloud (libgl1, libglib2.0-0)
├── app/
│   ├── Home.py               # Landing page (hero + KPIs)
│   ├── pages/                # Seven Streamlit pages
│   ├── ui.py                 # UI components (theme, cards)
│   ├── state.py              # Session state
│   └── utils.py              # ROOT path
├── src/
│   ├── infer/                # Inference engine
│   │   ├── predict_pt.py     # PyTorch inference
│   │   ├── predict_onnx.py   # ONNX inference
│   │   ├── event_packet.py   # Event packet generation
│   │   ├── webhook.py        # Webhook client
│   │   └── runtime.py        # Model loading
│   ├── train/                # Training scripts
│   ├── convert/              # Dataset conversion
│   └── utils/                # Hashing, timing, NMS, image
├── models/weights/           # best.pt / best.onnx (gitignored)
├── datasets/                 # Training data (gitignored)
├── pages/                    # Proxy → app/pages/ (multi-page Streamlit)
├── scripts/                  # Utilities (download, resume, mock)
└── runs/                     # Training results
    └── summary.json          # Final metrics (versioned)
```

---

## Security and integrity

```
Image  -> SHA-256 -> input_hash
Model  -> SHA-256 -> model_hash
Packet -> SHA-256 -> packet_hash -> HMAC-SHA256(secret) -> signature
```

- **Reproducibility**: same input → same output (deterministic NMS, no randomness).
- **Traceability**: every packet contains the input hash, model hash and signature.
- **Verification**: HMAC-SHA256 with a shared secret.

---

## Orbital compatibility

| Profile | Compute | Power | Inference / tile | Reference |
|---|---|---|---|---|
| LP (Low Power) | Intel Myriad X | 1–2 W | 500–1000 ms | Φ-Sat-2 |
| HP (High Perf) | AMD64 + GPU | 15–25 W | 30–80 ms | Moog iX5 |

Target platform: D-Orbit ION Satellite Carrier (hosted payload).

- S-band telemetry ~500 kbps (sufficient for event packets)
- X-band telemetry > 50 Mbps (backup for evidence)
- In-orbit model update supported

---

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `EDGE_SPACE_HMAC_SECRET` | HMAC secret for packet signature | `demo-secret` |

Create a `.env` file at the project root (gitignored).

---

## License

Internal project — Thales Incubator.

---

*EDGE SPACE — Wildfire detection from satellite imagery using on-board AI · Thales Incubator*
