import streamlit as st
from utils.config import APP_NAME
from utils.storage import init_db

# -----------------------------------------------------
# Streamlit Page Setup
# -----------------------------------------------------
st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide")

# Ensure database and tables exist
init_db()

# -----------------------------------------------------
# App Overview
# -----------------------------------------------------
st.title("🧭 Single Reporting Tool")

st.markdown(
    """
Collect once, route everywhere. Use **Submit Report** to complete the dynamic form, 
then manage and export via **Admin Dashboard**.

**What this starter does**
- Implements your 5-step form with conditional logic (ABN, jurisdiction, purposes, ransomware branch)
- Saves submissions to local SQLite (dev) with optional file attachments
- Exports submissions to CSV/JSON and generates destination-shaped JSON stubs
- Simple search & filters in the dashboard

> 💡 Tip: This is a developer starter. Put it behind your organisation’s auth before deploying.
"""
)

st.info("Use the left sidebar to switch pages.")
