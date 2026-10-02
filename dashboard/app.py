import streamlit as st

st.set_page_config(
    page_title="CareInsights",
    page_icon="📊",
    layout="wide",
)

st.title("CareInsights")
st.caption("Healthcare Analytics & Clinical Intelligence")

st.info(
    "Repository scaffold initialized. The 30-Day Readmission Intelligence dashboard is the first UI module to be connected to PostgreSQL."
)

st.subheader("Modules")
st.write("• 30-Day Readmissions — next milestone")
st.write("• Executive Overview — planned")
st.write("• Department Performance — planned")
st.write("• ICU Intelligence — planned")
st.write("• Patient Analytics — planned")
