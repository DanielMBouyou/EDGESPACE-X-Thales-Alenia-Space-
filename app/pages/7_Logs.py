from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE - Logs", layout="wide")
apply_theme()
init_state()

header("Logs", "Recent event packets and webhook responses.")

st.markdown("**Events sent**")
if st.session_state.events_log:
    st.dataframe(pd.DataFrame(st.session_state.events_log))
else:
    st.info("No events sent yet.")

st.markdown("**Webhook errors**")
if st.session_state.errors_log:
    st.dataframe(pd.DataFrame(st.session_state.errors_log))
else:
    st.info("No errors logged.")
