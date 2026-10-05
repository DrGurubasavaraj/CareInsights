import streamlit as st

from db import query_df


st.set_page_config(
    page_title="CareInsights",
    page_icon="📊",
    layout="wide",
)

st.title("CareInsights")
st.caption("Healthcare Analytics & Clinical Intelligence")

st.subheader("30-Day Readmission Intelligence")

try:
    kpi = query_df(
        """
        SELECT
            thirty_day_readmissions,
            total_eligible_discharges,
            readmission_rate_pct
        FROM vw_readmission_kpi;
        """
    )

    metadata = query_df(
        """
        SELECT observation_end_date
        FROM dataset_metadata
        ORDER BY dataset_id DESC
        LIMIT 1;
        """
    )

except Exception:
    st.error(
        "CareInsights could not connect to PostgreSQL. "
        "Create .streamlit/secrets.toml from the provided example "
        "and verify that the local hospital_analytics database is running."
    )
    st.stop()


if kpi.empty:
    st.warning("vw_readmission_kpi returned no rows.")
    st.stop()


row = kpi.iloc[0]

readmission_rate = float(row["readmission_rate_pct"])
readmissions = int(row["thirty_day_readmissions"])
eligible_discharges = int(row["total_eligible_discharges"])

observation_end = "Unavailable"
if not metadata.empty:
    observation_end = metadata.iloc[0]["observation_end_date"].strftime("%d %b %Y")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="30-Day Readmission Rate",
        value=f"{readmission_rate:.2f}%",
    )

with col2:
    st.metric(
        label="30-Day Readmissions",
        value=f"{readmissions:,}",
    )

with col3:
    st.metric(
        label="Eligible Discharges",
        value=f"{eligible_discharges:,}",
    )

with col4:
    st.metric(
        label="Dataset Through",
        value=observation_end,
    )

st.caption(
    "Synthetic portfolio dataset. Readmission KPI includes only index "
    "discharges with a complete 30-day observation window."
)

st.divider()

st.info(
    "Milestone 1: PostgreSQL → validated analytical view → Streamlit KPI cards. "
    "Monthly trend, department comparison, transition analysis and patient "
    "drill-down will be added next."
)
