"""Resume training from last checkpoint — memory-safe version."""
from ultralytics import YOLO
from pathlib import Path

LAST_PT = (
    Path(r"C:\Users\danie\OneDrive\Documents\IA\space-edge-fire-detector")
    / "runs" / "detect" / "runs"
    / "fire_detection_s_20260209_105044"
    / "weights" / "last.pt"
)

if not LAST_PT.exists():
    raise FileNotFoundError(f"Checkpoint not found: {LAST_PT}")

print(f"Resuming from: {LAST_PT}")
model = YOLO(str(LAST_PT))
model.train(resume=True, workers=0)  # workers=0 = no subprocess = less RAM
