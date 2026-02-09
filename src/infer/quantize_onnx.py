from __future__ import annotations

import argparse
from pathlib import Path

from onnxruntime.quantization import QuantType, quantize_dynamic


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Quantize ONNX model (dynamic INT8)")
    p.add_argument("--onnx", required=True, help="Input ONNX path")
    p.add_argument("--out", required=True, help="Output INT8 ONNX path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    inp = Path(args.onnx)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    quantize_dynamic(
        model_input=str(inp),
        model_output=str(out),
        weight_type=QuantType.QInt8,
    )

    print(f"Quantized model saved to {out}")


if __name__ == "__main__":
    main()
