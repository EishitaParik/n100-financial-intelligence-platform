import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 N100 Financial Intelligence Platform")
st.markdown("""
Welcome to the **Nifty 100 Financial Intelligence Platform**.

Use the navigation menu on the left to access:

- 🏠 Home
- 🏢 Company Profile
- 🔍 Screener
- 👥 Peer Comparison
- 📈 Trend Analysis
- 🏭 Sector Analysis
- 💰 Capital Allocation
- 📄 Annual Reports
""")

st.success("Dashboard loaded successfully.")
