from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "app" / "pages" / "1_Try_it.py"),
    run_name="__main__",
)
