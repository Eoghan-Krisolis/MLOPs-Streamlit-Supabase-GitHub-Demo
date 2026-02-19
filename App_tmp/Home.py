import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

st.title("MLOps Demo")
st.write("Use the sidebar for inference and monitoring.")
