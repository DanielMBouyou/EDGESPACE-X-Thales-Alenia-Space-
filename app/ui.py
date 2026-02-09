from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
  font-family: 'Space Grotesk', sans-serif;
}

.stApp {
  background: radial-gradient(1200px 800px at 10% 10%, #f2f7ff 0%, #f6f2ff 35%, #fff6ef 70%, #f7fbff 100%);
}

.edge-card {
  background: linear-gradient(180deg, #ffffff 0%, #f7f7ff 100%);
  border: 1px solid #e3e3f5;
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 10px 30px rgba(12, 14, 40, 0.08);
}

.edge-title {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 6px 0;
}

.edge-subtitle {
  font-size: 16px;
  color: #4b4f6b;
}

.edge-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #0b1a3a;
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.edge-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  background: #0b1a3a;
  color: #b6ffef;
  padding: 12px;
  border-radius: 12px;
}

.edge-step {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
  border: 1px solid #e7e7ff;
  background: #ffffff;
}

.edge-step.ok {
  background: #e5fff4;
  border-color: #a8f0d6;
}

.edge-step.warn {
  background: #fff6dd;
  border-color: #ffe4a1;
}

.edge-step.off {
  background: #f1f1f5;
  border-color: #e4e4ef;
  color: #7c7c8f;
}
</style>
""",
        unsafe_allow_html=True,
    )


def header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="edge-card">
  <div class="edge-pill">EDGE SPACE</div>
  <div class="edge-title">{title}</div>
  <div class="edge-subtitle">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str) -> None:
    st.markdown(
        f"""
<div class="edge-card">
  <div style="font-weight:600;font-size:18px;margin-bottom:8px;">{title}</div>
  <div style="color:#4b4f6b;">{body}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def pipeline_bar(steps: list[tuple[str, str]]) -> None:
    chips = []
    for name, status in steps:
        cls = "edge-step"
        if status == "ok":
            cls += " ok"
        elif status == "warn":
            cls += " warn"
        else:
            cls += " off"
        chips.append(f"<span class=\"{cls}\">{name}</span>")
    st.markdown(
        f"<div style='display:flex;gap:8px;flex-wrap:wrap'>{''.join(chips)}</div>",
        unsafe_allow_html=True,
    )
