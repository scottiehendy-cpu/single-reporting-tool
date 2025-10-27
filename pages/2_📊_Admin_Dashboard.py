import streamlit as st
from utils.storage import fetch_reports_df, purge_all, get_destination_json

st.title("📊 Admin Dashboard")

with st.expander("Filters", expanded=True):
    q = st.text_input("Free text search (ref, reporter, org, summary)…")

col1, col2, col3 = st.columns([3,1,1])
with col1:
    df = fetch_reports_df(q)
    st.caption(f"{len(df)} records")
    st.dataframe(df, use_container_width=True, hide_index=True)
with col2:
    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False),
        file_name="reports.csv",
        mime="text/csv",
        use_container_width=True,
    )
with col3:
    if st.button("🗑️ Purge (dev only)", help="Deletes all records and files"):
        purge_all()
        st.warning("All data removed (dev only). Reload page.")

st.markdown("---")
st.subheader("Destination Exports")

dest = st.selectbox(
    "Choose a destination schema to preview",
    ["ACSC", "HomeAffairs", "OAIC", "APRA", "ASIC", "RBA", "ACCC/CDR", "TGA"],
)
idx = st.number_input("Report ID", min_value=1, step=1)
if st.button("Generate JSON", use_container_width=True):
    try:
        js = get_destination_json(int(idx), dest)
        st.code(js, language="json")
        st.download_button(
            label=f"Download {dest} JSON",
            data=js,
            file_name=f"report_{idx}_{dest}.json",
            mime="application/json",
            use_container_width=True,
        )
    except Exception as e:
        st.error(str(e))
