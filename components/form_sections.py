import streamlit as st
from utils.validators import is_valid_abn

# ---------- constants ----------
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

# ---------- sections ----------
def reporter_section(prefill: dict | None = None):
    pre = prefill or {}
    c1, c2 = st.columns(2)
    with c1:
        first_name = st.text_input("First name *",
                                   value=pre.get("first_name",""),
                                   help="Person we can contact about this report.")
        title = st.text_input("Title", value=pre.get("title",""))
        email = st.text_input("Email address *",
                              value=pre.get("email",""),
                              help="We’ll send confirmations and follow-ups here.")
    with c2:
        surname = st.text_input("Surname *", value=pre.get("surname",""))
        phone = st.text_input("Phone number *",
                              value=pre.get("phone",""),
                              help="Include country/area code if outside AU.")
    return {
        "first_name": first_name.strip(),
        "surname": surname.strip(),
        "title": title.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
    }

def organisation_section(prefill: dict | None = None):
    pre = prefill or {}
    name = st.text_input("Organisation name *", value=pre.get("name",""))

    abn_default = "Has ABN" if pre.get("abn_status","has_abn") == "has_abn" else "Not applicable"
    abn_status = st.segmented_control(
        "ABN", ["Has ABN", "Not applicable"], selection_mode="single", help="Australian Business Number",
        default=abn_default
    )
    abn = pre.get("abn","")
    abn_reason = pre.get("abn_reason","")
    if abn_status == "Has ABN":
        abn = st.text_input("ABN *", value=abn, placeholder="11 222 333 444",
                            help="If unsure, check abr.business.gov.au")
        if abn and not is_valid_abn(abn):
            st.warning("ABN format looks unusual. Continue if correct.")
    else:
        abn_reason = st.text_input("Why is an ABN not applicable? *", value=abn_reason)

    jurisdiction = st.selectbox("State/Territory or Overseas *", STATES,
                                index=max(0, STATES.index(pre.get("jurisdiction","ACT"))),
                                help="If 'ACT' we’ll ask for a postcode; if 'Overseas' we’ll ask for a country.")
    postcode = pre.get("postcode","")
    country = pre.get("country","")
    if jurisdiction == "ACT":
        postcode = st.text_input("Postcode *", value=postcode)
    elif jurisdiction == "Overseas":
        country = st.text_input("Country *", value=country)

    address = st.text_input("Organisation address *", value=pre.get("address",""))
    secondary_email = st.text_input("Secondary email", value=pre.get("secondary_email",""))
    website = st.text_input("Website address", value=pre.get("website",""))

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

def purpose_section(prefill: dict | None = None):
    pre = prefill or {}
    purposes = st.multiselect("Purpose(s) for reporting *", PURPOSES, default=pre.get("purposes", []))

    cs_reason = pre.get("cybersecurity_reason", [])
    ci_member = pre.get("ci_member")
    ci_sectors = pre.get("ci_sectors", [])
    consent_home_affairs = pre.get("consent_home_affairs")

    if "Cybersecurity Incident" in purposes:
        st.markdown("**Cybersecurity Incident details**")
        cs_reason = st.multiselect("Reason for reporting",
                                   ["Inform ACSC", "Request ACSC assistance"],
                                   default=cs_reason)
        ci_member = st.selectbox("Are you a Critical Infrastructure (CI) sector member? *",
                                 ["Yes","No","Unsure"],
                                 index={"Yes":0,"No":1,"Unsure":2}.get(ci_member or "No",1))
        if ci_member == "Yes":
            ci_sectors = st.multiselect("Select CI sector(s) *", CI_SECTORS, default=ci_sectors)
        consent_home_affairs = st.selectbox("Consent to share details with Home Affairs? *",
                                            ["Yes","No"],
                                            index=0 if (consent_home_affairs or "No")=="Yes" else 1)

    return {
        "purposes": purposes,
        "cybersecurity_reason": cs_reason,
        "ci_member": ci_member,
        "ci_sectors": ci_sectors,
        "consent_home_affairs": consent_home_affairs,
    }

def incident_section(purpose_dict: dict, prefill: dict | None = None):
    pre = prefill or {}
    itype = st.selectbox("Incident type *", INCIDENT_TYPES,
                         index=max(0, INCIDENT_TYPES.index(pre.get("type","Denial of service (DoS/DDoS)"))))
    other_text = pre.get("other_type_text","")
    if itype == "Other":
        other_text = st.text_input("If Other, please specify *", value=other_text)

    infra_impacted = st.selectbox("Impacted infrastructure/systems? *", ["Yes","No"],
                                  index=0 if (pre.get("infra_impacted")=="Yes") else 1)
    infra_details = pre.get("infra_impact_details","")
    if infra_impacted == "Yes":
        infra_details = st.text_area("Outline the impact *", value=infra_details, height=100)

    cust_impacted = st.selectbox("Impacted customers? *", ["Yes","No","Unknown"],
                                 index={"Yes":0,"No":1,"Unknown":2}.get(pre.get("customers_impacted","Unknown"),2))

    c1, c2 = st.columns(2)
    with c1:
        occ_date = st.date_input("Occurrence date *", value=st.session_state.get("occ_date") or None)
        occ_time = st.time_input("Occurrence time *", value=None)
        ongoing = st.selectbox("Is the incident ongoing? *", ["Yes","No","Unknown"],
                               index={"Yes":0,"No":1,"Unknown":2}.get(pre.get("ongoing","Unknown"),2))
    with c2:
        id_date = st.date_input("Identification date *", value=None)
        id_time = st.time_input("Identification time *", value=None)
        identified_by = st.selectbox("How was it identified? *", ["Organisation","Third party"],
                                     index=0 if (pre.get("identified_by","Organisation")=="Organisation") else 1)

    narrative = st.text_area("Describe the incident (what, where, when, who, how) *",
                             value=pre.get("narrative",""), height=150)
    extra = st.text_area("Any further details that may assist the Commonwealth",
                         value=pre.get("additional_details",""), height=120)

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

def ransomware_section(prefill: dict | None = None):
    pre = prefill or {}
    variants = st.text_input("Ransomware variant(s) (comma-separated)", value=", ".join(pre.get("variants",[])))
    vulns = st.text_input("Exploited vulnerabilities (e.g., CVEs)", value=pre.get("exploited_vulns",""))
    demanded = st.text_input("Type of payment demanded (e.g., XMR/BTC) *", value=pre.get("payment_demanded",""))
    provided = st.text_input("Type of payment provided (if any)", value=pre.get("payment_provided",""))
    comms = st.selectbox("Any communication with the extorting entity? *", ["Yes","No","Unknown"],
                         index={"Yes":0,"No":1,"Unknown":2}.get(pre.get("communicated_with_extorter","Unknown"),2))
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

# ---------- progress helper ----------
def completion_percent(reporter, organisation, purpose, incident, ransomware):
    required = 0
    filled = 0

    for k in ["first_name","surname","email","phone"]:
        required += 1; filled += 1 if reporter.get(k) else 0

    required += 3
    filled += sum(bool(organisation.get(k)) for k in ["name","jurisdiction","address"])
    if organisation.get("abn_status") == "has_abn":
        required += 1; filled += 1 if organisation.get("abn") else 0
    else:
        required += 1; filled += 1 if organisation.get("abn_reason") else 0
    if organisation.get("jurisdiction") == "ACT":
        required += 1; filled += 1 if organisation.get("postcode") else 0
    if organisation.get("jurisdiction") == "Overseas":
        required += 1; filled += 1 if organisation.get("country") else 0

    required += 1; filled += 1 if purpose.get("purposes") else 0
    if "Cybersecurity Incident" in (purpose.get("purposes") or []):
        required += 2
        filled += bool(purpose.get("ci_member")) + bool(purpose.get("consent_home_affairs"))
        if purpose.get("ci_member") == "Yes":
            required += 1; filled += 1 if purpose.get("ci_sectors") else 0

    required += 10
    filled += sum(bool(incident.get(k)) for k in [
        "type","infra_impacted","customers_impacted","occurrence_date","occurrence_time",
        "identified_date","identified_time","ongoing","identified_by","narrative"
    ])
    if incident.get("type") == "Other":
        required += 1; filled += 1 if incident.get("other_type_text") else 0
    if incident.get("infra_impacted") == "Yes":
        required += 1; filled += 1 if incident.get("infra_impact_details") else 0

    if "Ransomware/Cyber Extortion Payment" in (purpose.get("purposes") or []):
        required += 2
        filled += bool((ransomware or {}).get("payment_demanded"))
        filled += bool((ransomware or {}).get("communicated_with_extorter"))

    return int(100 * filled / max(required, 1))
