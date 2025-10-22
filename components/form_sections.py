import streamlit as st
from utils.validators import is_valid_abn

STATES = ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA", "Overseas"]
INCIDENT_TYPES = [
    "Denial of service (DoS/DDoS)",
    "Reconnaissance / scanning",
    "Unauthorised access",
    "Data exposure / theft / leak",
    "Malware",
    "Ransomware",
    "Phishing / social engineering",
    "Service outage",
    "Supply chain compromise",
    "Exploit of unpatched vulnerability",
    "Other",
]
CI_SECTORS = [
    "Communications","Financial Services","Data Storage or Processing",
    "Defence","Education","Energy","Food & Grocery","Healthcare & Med",
    "Space","Transport","Water & Sewerage","Other",
]
PURPOSES = [
    "Cybersecurity Incident",
    "Data Breach Incident",
    "SSBA Incident",
    "CDR Info Incident",
    "Medical Device Incident",
    "Ransomware/Cyber Extortion Payment",
    "Information Security Incident",
    "Breach in Financial Stability Standards",
    "Incident Affecting Licensees",
]

def reporter_section():
    c1, c2 = st.columns(2)
    with c1:
        first_name = st.text_input("First name *")
        title = st.text_input("Title")
        email = st.text_input("Email address *")
    with c2:
        surname = st.text_input("Surname *")
        phone = st.text_input("Phone number *")
    return {
        "first_name": first_name.strip(),
        "surname": surname.strip(),
        "title": title.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
    }

def organisation_section():
    name = st.text_input("Organisation name *")

    abn_status = st.segmented_control("ABN", ["Has ABN", "Not applicable"], selection_mode="single")
    abn = abn_reason = ""
    if abn_status == "Has ABN":
        abn = st.text_input("ABN *", placeholder="11 222 333 444")
        if abn and not is_valid_abn(abn):
            st.warning("ABN format looks unusual. Continue if correct.")
    else:
        abn_reason = st.text_input("Why is an ABN not applicable? *")

    jurisdiction = st.selectbox("State/Territory or Overseas *", STATES)
    postcode = country = ""
    if jurisdiction == "ACT":
        postcode = st.text_input("Postcode *")
    elif jurisdiction == "Overseas":
        country = st.text_input("Country *")

    address = st.text_input("Organisation address *")
    secondary_email = st.text_input("Secondary email")
    website = st.text_input("Website address")

    return {
        "name": name.strip(),
        "abn_status": "has_abn" if abn_status == "Has ABN" else "not_applicable",
        "abn": abn.strip(),
        "abn_reason": abn_reason.strip(),
        "jurisdiction": jurisdiction,
        "postcode": postcode.strip(),
        "country": country.strip(),
        "address": address.strip(),
        "secondary_email": secondary_email.strip(),
        "website": website.strip(),
    }

def purpose_section():
    purposes = st.multiselect("Purpose(s) for reporting *", PURPOSES)

    cs_reason = []
    ci_member = None
    ci_sectors = []
    consent_home_affairs = None

    if "Cybersecurity Incident" in purposes:
        st.markdown("**Cybersecurity Incident details**")
        cs_reason = st.multiselect("Reason for reporting", ["Inform ACSC", "Request ACSC assistance"])
        ci_member = st.selectbox("Are you a Critical Infrastructure (CI) sector member? *", ["Yes","No","Unsure"], index=1)
        if ci_member == "Yes":
            ci_sectors = st.multiselect("Select CI sector(s) *", CI_SECTORS)
        consent_home_affairs = st.selectbox("Consent to share details with Home Affairs? *", ["Yes","No"], index=1)

    return {
        "purposes": purposes,
        "cybersecurity_reason": cs_reason,
        "ci_member": ci_member,
        "ci_sectors": ci_sectors,
        "consent_home_affairs": consent_home_affairs,
    }

def incident_section(purpose_dict: dict):
    itype = st.selectbox("Incident type *", INCIDENT_TYPES)
    other_text = ""
    if itype == "Other":
        other_text = st.text_input("If Other, please specify *")

    infra_impacted = st.selectbox("Impacted infrastructure/systems? *", ["Yes","No"])
    infra_details = ""
    if infra_impacted == "Yes":
        infra_details = st.text_area("Outline the impact *", height=100)

    cust_impacted = st.selectbox("Impacted customers? *", ["Yes","No","Unknown"])

    c1, c2 = st.columns(2)
    with c1:
        occ_date = st.date_input("Occurrence date *")
        occ_time = st.time_input("Occurrence time *")
        ongoing = st.selectbox("Is the incident ongoing? *", ["Yes","No","Unknown"], index=1)
    with c2:
        id_date = st.date_input("Identification date *")
        id_time = st.time_input("Identification time *")
        identified_by = st.selectbox("How was it identified? *", ["Organisation","Third party"])

    narrative = st.text_area("Describe the incident (what, where, when, who, how) *", height=150)
    extra = st.text_area("Any further details that may assist the Commonwealth", height=120)

    return {
        "type": itype,
        "other_type_text": other_text,
        "infra_impacted": infra_impacted,
        "infra_impact_details": infra_details,
        "customers_impacted": cust_impacted,
        "occurrence_date": str(occ_date),
        "occurrence_time": occ_time.strftime("%H:%M:%S"),
        "identified_date": str(id_date),
        "identified_time": id_time.strftime("%H:%M:%S"),
        "ongoing": ongoing,
        "identified_by": identified_by,
        "narrative": narrative,
        "additional_details": extra,
    }

def ransomware_section():
    variants = st.text_input("Ransomware variant(s) (comma-separated)")
    vulns = st.text_input("Exploited vulnerabilities (e.g., CVEs)")
    demanded = st.text_input("Type of payment demanded (e.g., XMR/BTC) *")
    provided = st.text_input("Type of payment provided (if any)")
    comms = st.selectbox("Any communication with the extorting entity? *", ["Yes","No","Unknown"], index=2)
    return {
        "variants": [v.strip() for v in variants.split(",") if v.strip()],
        "exploited_vulns": vulns,
        "payment_demanded": demanded,
        "payment_provided": provided,
        "communicated_with_extorter": comms,
    }

def attachments_section():
    files = st.file_uploader("Upload supporting files (PDF, CSV, images, logs)",
                             type=["pdf","csv","png","jpg","jpeg","txt"],
                             accept_multiple_files=True)
    return files or []

def review_section(reporter, organisation, purpose, incident, ransomware):
    st.caption("Review your responses before submitting.")
    with st.expander("Preview JSON", expanded=False):
        import json
        payload = {
            "reporter": reporter,
            "organisation": organisation,
            "purpose": purpose,
            "incident": incident,
            "ransomware": ransomware,
        }
        st.code(json.dumps(payload, indent=2), language="json")
