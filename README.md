# EDGE SPACE - Prototype A-Z

Demo: SAR vessel detection -> event packet -> webhook.

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

## Data

1. Put raw SARFish data in `datasets/raw/`.
2. Convert + split:

```bash
python src/convert/sarfish_to_yolo.py --input datasets/raw --output datasets/yolo
python src/convert/split.py --yolo datasets/yolo --seed 42
```

This produces `datasets/dataset.yaml`.

## Train

```bash
python src/train/train_yolo.py --data datasets/dataset.yaml --model yolov8n.pt --epochs 50
```

Weights: `models/weights/best.pt`

## Export + Orbit Inference

```bash
python src/infer/export_onnx.py --weights models/weights/best.pt --out models/weights/best.onnx
python src/infer/quantize_onnx.py --onnx models/weights/best.onnx --out models/weights/best.int8.onnx
```

## Run Streamlit

```bash
streamlit run app/Home.py
```

## Mock Webhook (optional)

```bash
python scripts/mock_webhook.py
```

## Notes

- Event packets are JSON-only (no image downlink).
- `datasets/demo_samples/` contains demo chips.
- Set `EDGE_SPACE_HMAC_SECRET` (or use `.env`) to customize packet signatures.
