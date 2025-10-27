import streamlit as st
from components.form_sections import (
    reporter_section, organisation_section, purpose_section,
    incident_section, ransomware_section, review_section,
    attachments_section, completion_percent,
)
from utils.models import Report
from utils.storage import save_report, save_draft, load_draft, submit_from_ref

st.title("📄 Submit Report")

# --- tiny helpers for query params (back/forward compatible) ---
def get_qp():
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()

def set_qp(**kwargs):
    try:
        st.query_params.update(kwargs)
    except Exception:
        st.experimental_set_query_params(**kwargs)

# --- Resume draft ---
qp = get_qp()
ref_in_url = (qp.get("ref") if isinstance(qp.get("ref"), str) else (qp.get("ref",[None])[0] if qp.get("ref") else None))

with st.expander("Resume a saved draft", expanded=bool(ref_in_url)):
    ref_input = st.text_input("Enter your reference code", value=ref_in_url or "")
    if st.button("Load draft"):
        data = load_draft((ref_input or "").strip().upper())
        if data:
            st.session_state["form_state"] = data
            st.success("Draft loaded. Scroll down to continue.")
        else:
            st.error("No draft found for that reference.")

prefill = st.session_state.get("form_state") or {}

with st.form("report_form", clear_on_submit=False):
    st.subheader("1) Contact Officer Details")
    reporter = reporter_section(prefill.get("reporter"))

    st.subheader("2) Organisation Details")
    organisation = organisation_section(prefill.get("organisation"))

    st.subheader("3) Purpose for Reporting")
    purpose = purpose_section(prefill.get("purpose"))

    st.subheader("4) Incident Discovery & Details")
    incident = incident_section(purpose, prefill.get("incident"))

    ransomware = None
    if "Ransomware/Cyber Extortion Payment" in purpose.get("purposes", []):
        st.subheader("4a) Ransomware / Extortion Details")
        ransomware = ransomware_section((prefill or {}).get("ransomware"))

    st.subheader("Attachments (optional)")
    attachments = attachments_section()

    st.subheader("5) Review & Submit")
    review_section(reporter, organisation, purpose, incident, ransomware)

    pct = completion_percent(reporter, organisation, purpose, incident, ransomware)
    st.progress(pct, text=f"{pct}% complete")

    colA, colB = st.columns(2)
    with colA:
        submitted = st.form_submit_button("Submit report", use_container_width=True)
    with colB:
        savedraft = st.form_submit_button("💾 Save for later", use_container_width=True)

if savedraft:
    payload = {
        "reporter": reporter, "organisation": organisation,
        "purpose": purpose, "incident": incident, "ransomware": ransomware,
    }
    ref = save_draft(payload, ref_in_url)
    set_qp(ref=ref)
    st.success(f"Draft saved. Reference: {ref}")
    st.link_button("Open draft link", url=f"?ref={ref}", use_container_width=True)

if submitted:
    try:
        if ref_in_url:
            row_id = submit_from_ref(ref_in_url)
        else:
            report = Report(reporter=reporter, organisation=organisation,
                            purpose=purpose, incident=incident, ransomware=ransomware)
            row_id = save_report(report, attachments)
        st.success(f"Report submitted with ID {row_id}.")
        st.download_button(
            "Download JSON copy",
            data=Report(reporter=reporter, organisation=organisation,
                       purpose=purpose, incident=incident, ransomware=ransomware
                       ).model_dump_json(indent=2),
            file_name=f"report_{row_id}.json",
            mime="application/json",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not save: {e}")
