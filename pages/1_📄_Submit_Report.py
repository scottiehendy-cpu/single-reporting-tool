import streamlit as st
from components.form_sections import (
    reporter_section,
    organisation_section,
    purpose_section,
    incident_section,
    ransomware_section,
    review_section,
    attachments_section,
)
from utils.models import Report
from utils.storage import save_report

st.title("📄 Submit Report")

# Persist form state across reruns (optional)
if "form_state" not in st.session_state:
    st.session_state.form_state = {}

with st.form("report_form", clear_on_submit=False):
    st.subheader("1) Contact Officer Details")
    reporter = reporter_section()

    st.subheader("2) Organisation Details")
    organisation = organisation_section()

    st.subheader("3) Purpose for Reporting")
    purpose = purpose_section()

    st.subheader("4) Incident Discovery & Details")
    incident = incident_section(purpose)

    # Conditional ransomware branch
    ransomware = None
    if "Ransomware/Cyber Extortion Payment" in purpose.get("purposes", []):
        st.subheader("4a) Ransomware / Extortion Details")
        ransomware = ransomware_section()

    st.subheader("Attachments (optional)")
    attachments = attachments_section()

    st.subheader("5) Review & Submit")
    review_section(reporter, organisation, purpose, incident, ransomware)

    submitted = st.form_submit_button("Submit report", use_container_width=True)

if submitted:
    try:
        report = Report(
            reporter=reporter,
            organisation=organisation,
            purpose=purpose,
            incident=incident,
            ransomware=ransomware,
        )
        row_id = save_report(report, attachments)
        st.success(f"Report saved with ID {row_id}.")
        st.download_button(
            "Download JSON copy",
            data=report.model_dump_json(indent=2),
            file_name=f"report_{row_id}.json",
            mime="application/json",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not save: {e}")
