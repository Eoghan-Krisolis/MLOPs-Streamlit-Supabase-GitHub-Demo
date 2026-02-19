import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

st.title("MLOps Demo")
st.write("Use the sidebar for inference and monitoring.")
