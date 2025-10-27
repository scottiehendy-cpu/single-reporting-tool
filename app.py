import streamlit as st
from utils.config import APP_NAME
from utils.storage import init_db

st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide")
init_db()

st.title("🧭 Single Reporting Tool")

st.markdown(
    """
Collect once, route everywhere. Use **Submit Report** to complete the dynamic form, then manage and export via **Admin Dashboard**.

**What this starter does**
- Implements your 5-step form with conditional logic (ABN, jurisdiction, purposes, ransomware branch)
- Saves submissions to local SQLite (dev) with optional file attachments
- Exports submissions to CSV/JSON and generates destination-shaped JSON stubs
- “Save for later” drafts with a short reference code (`?ref=AB12CD34`)
- Live **progress bar** for form completion
"""
)

st.info("Use the left sidebar to switch pages.")
