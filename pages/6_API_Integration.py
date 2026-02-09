from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "app" / "pages" / "6_API_Integration.py"),
    run_name="__main__",
)
