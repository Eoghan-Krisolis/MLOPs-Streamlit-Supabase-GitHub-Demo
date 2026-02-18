import streamlit as st
from src.config import MONITORING_DIR

st.title("Drift Monitoring")

path = MONITORING_DIR / "drift_report.html"

if path.exists():
    st.components.v1.html(path.read_text(), height=900, scrolling=True)
else:
    st.write("No drift report available.")
