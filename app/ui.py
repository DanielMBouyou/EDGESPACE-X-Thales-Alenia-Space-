from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-feature-settings: 'ss01', 'cv11';
  letter-spacing: -0.01em;
}

.stApp {
  background: #ffffff;
  color: #171a20;
}

h1, h2, h3, h4, h5, h6 {
  color: #171a20;
  font-weight: 600;
  letter-spacing: -0.02em;
}

p, li, span, label, div {
  color: #171a20;
}

a {
  color: #171a20;
  text-decoration: underline;
  text-underline-offset: 3px;
}

[data-testid="stMarkdownContainer"] code {
  font-family: 'IBM Plex Mono', monospace;
  background: #f4f4f5;
  color: #171a20;
  padding: 1px 6px;
  border-radius: 0;
  font-size: 0.9em;
}

.stButton > button, .stDownloadButton > button {
  border-radius: 0 !important;
  border: 1px solid #171a20;
  background: #ffffff;
  color: #171a20;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  font-size: 12px;
  padding: 10px 20px;
  transition: background 120ms ease, color 120ms ease;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  background: #171a20;
  color: #ffffff;
}

.stButton > button[kind="primary"] {
  background: #171a20;
  color: #ffffff;
}

.stButton > button[kind="primary"]:hover {
  background: #393c41;
}

input, textarea, select,
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox > div > div, .stMultiSelect > div > div {
  border-radius: 0 !important;
  border: 1px solid #d0d0d2 !important;
  background: #ffffff !important;
  color: #171a20 !important;
}

.stRadio label, .stCheckbox label {
  color: #171a20;
}

[data-testid="stMetricValue"] {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: #171a20;
  letter-spacing: -0.02em;
}

[data-testid="stMetricLabel"] {
  color: #5c5e62;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.08em;
}

[data-testid="stTable"] table, [data-testid="stDataFrame"] table {
  border-radius: 0;
  border-collapse: collapse;
}

[data-testid="stTable"] th, [data-testid="stDataFrame"] th {
  background: #f4f4f5;
  color: #171a20;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #d0d0d2;
}

hr, [data-testid="stDivider"] {
  border-top: 1px solid #e5e5e5;
}

.edge-card {
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 0;
  padding: 24px;
  box-shadow: none;
}

.edge-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.025em;
  margin: 0 0 8px 0;
  color: #171a20;
}

.edge-subtitle {
  font-size: 15px;
  color: #5c5e62;
  font-weight: 400;
  line-height: 1.5;
}

.edge-pill {
  display: inline-block;
  padding: 4px 10px;
  border: 1px solid #171a20;
  border-radius: 0;
  background: #ffffff;
  color: #171a20;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 500;
  margin-bottom: 12px;
}

.edge-code {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  background: #171a20;
  color: #f4f4f5;
  padding: 16px;
  border-radius: 0;
}

.edge-step {
  padding: 6px 12px;
  border-radius: 0;
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border: 1px solid #d0d0d2;
  background: #ffffff;
  color: #5c5e62;
  font-weight: 500;
}

.edge-step.ok {
  background: #171a20;
  border-color: #171a20;
  color: #ffffff;
}

.edge-step.warn {
  background: #ffffff;
  border-color: #171a20;
  color: #171a20;
}

.edge-step.off {
  background: #f4f4f5;
  border-color: #e5e5e5;
  color: #a0a0a3;
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
  <div style="font-weight:600;font-size:16px;margin-bottom:8px;color:#171a20;">{title}</div>
  <div style="color:#5c5e62;font-size:14px;line-height:1.6;">{body}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
<div class="edge-card" style="text-align:left;">
  <div style="font-size:11px;color:#5c5e62;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">{title}</div>
  <div style="font-size:28px;font-weight:600;color:#171a20;letter-spacing:-0.02em;">{value}</div>
  <div style="font-size:13px;color:#5c5e62;margin-top:4px;">{subtitle}</div>
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
