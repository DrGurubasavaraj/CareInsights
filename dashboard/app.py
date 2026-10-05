import plotly.graph_objects as go
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

    monthly = query_df(
        """
        SELECT
            discharge_month,
            eligible_discharges,
            thirty_day_readmissions,
            monthly_readmission_pct,
            month_completeness
        FROM vw_readmission_monthly_trend
        ORDER BY discharge_month;
        """
    )

    department = query_df(
        """
        SELECT
            department,
            eligible_discharges,
            thirty_day_readmissions,
            dept_readmission_pct,
            hospital_readmission_pct,
            variance_from_hospital_pp
        FROM vw_readmission_by_department
        ORDER BY dept_readmission_pct;
        """
    )

    department_transition = query_df(
        """
        SELECT
            department_transition,
            readmission_count,
            total_readmissions,
            department_transition_pct
        FROM vw_readmission_department_transition
        ORDER BY department_transition_pct;
        """
    )

    diagnosis_transition = query_df(
        """
        SELECT
            diagnosis_transition,
            readmission_count,
            total_readmissions,
            diagnosis_transition_pct
        FROM vw_readmission_diagnosis_transition
        ORDER BY diagnosis_transition_pct;
        """
    )

    registry = query_df(
        """
        SELECT
            c.patient_id,
            c.patient_name,
            p.age,
            p.gender,
            p.city,
            c.index_discharge_date,
            c.next_admission_date,
            c.days_to_readmission,
            c.index_department,
            c.index_diagnosis,
            p.admission_type AS index_admission_type,
            p.bill_amount AS index_bill_amount,
            c.readmission_department,
            c.readmission_diagnosis,
            c.department_transition,
            c.diagnosis_transition,
            c.readmission_type,
            c.readmission_bill_amount
        FROM vw_readmission_encounter_comparison c
        JOIN vw_readmission_patient_registry p
          ON c.patient_id = p.patient_id
         AND c.next_admission_id = p.next_admission_id
        ORDER BY
            c.days_to_readmission,
            c.patient_id;
        """
    )

except Exception as exc:
    st.error(
        "CareInsights could not load data from PostgreSQL. "
        "Verify that hospital_analytics is running and that the analytical "
        "views are available."
    )
    st.code(str(exc))
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


# ---------------------------------------------------------------------------
# Executive KPI row
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Monthly trend + department comparison
# ---------------------------------------------------------------------------

trend_col, dept_col = st.columns([1.15, 1], gap="large")


with trend_col:
    st.markdown("### Monthly Readmission Trend")

    complete_months = monthly[
        monthly["month_completeness"] == "Complete Month"
    ].copy()

    if complete_months.empty:
        st.info("No complete monthly cohorts are available.")
    else:
        complete_months["monthly_readmission_pct"] = complete_months[
            "monthly_readmission_pct"
        ].astype(float)

        trend_fig = go.Figure()

        trend_fig.add_trace(
            go.Scatter(
                x=complete_months["discharge_month"],
                y=complete_months["monthly_readmission_pct"],
                mode="lines+markers",
                name="Monthly rate",
                line=dict(width=3),
                marker=dict(size=8),
                customdata=complete_months[
                    ["eligible_discharges", "thirty_day_readmissions"]
                ],
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>"
                    "Readmission rate: %{y:.2f}%<br>"
                    "Readmissions: %{customdata[1]:,.0f}<br>"
                    "Eligible discharges: %{customdata[0]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        trend_fig.add_hline(
            y=readmission_rate,
            line_dash="dash",
            line_width=2,
            annotation_text=f"Hospital rate {readmission_rate:.2f}%",
            annotation_position="top left",
        )

        trend_fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=25, b=10),
            showlegend=False,
            hovermode="x unified",
            xaxis_title=None,
            yaxis_title="Readmission rate (%)",
            yaxis=dict(
                rangemode="tozero",
                ticksuffix="%",
                gridcolor="rgba(15, 23, 42, 0.08)",
            ),
            xaxis=dict(
                tickformat="%b %y",
                showgrid=False,
            ),
        )

        st.plotly_chart(
            trend_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.caption(
            "Complete calendar-month cohorts only. Partial boundary months "
            "remain in the analytical view but are excluded from this trend."
        )


with dept_col:
    st.markdown("### Department Comparison")

    if department.empty:
        st.info("No department-level readmission data are available.")
    else:
        department = department.copy()
        department["dept_readmission_pct"] = department[
            "dept_readmission_pct"
        ].astype(float)
        department["variance_from_hospital_pp"] = department[
            "variance_from_hospital_pp"
        ].astype(float)

        department = department.sort_values(
            "dept_readmission_pct",
            ascending=True,
        )

        dept_fig = go.Figure()

        dept_fig.add_trace(
            go.Bar(
                x=department["dept_readmission_pct"],
                y=department["department"],
                orientation="h",
                name="Department rate",
                customdata=department[
                    [
                        "eligible_discharges",
                        "thirty_day_readmissions",
                        "variance_from_hospital_pp",
                    ]
                ],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Readmission rate: %{x:.2f}%<br>"
                    "Readmissions: %{customdata[1]:,.0f}<br>"
                    "Eligible discharges: %{customdata[0]:,.0f}<br>"
                    "Variance vs hospital: %{customdata[2]:+.2f} pp"
                    "<extra></extra>"
                ),
            )
        )

        dept_fig.add_vline(
            x=readmission_rate,
            line_dash="dash",
            line_width=2,
            annotation_text=f"Hospital {readmission_rate:.2f}%",
            annotation_position="top",
        )

        dept_fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=25, b=10),
            showlegend=False,
            xaxis_title="30-day readmission rate (%)",
            yaxis_title=None,
            xaxis=dict(
                rangemode="tozero",
                ticksuffix="%",
                gridcolor="rgba(15, 23, 42, 0.08)",
            ),
            yaxis=dict(showgrid=False),
        )

        st.plotly_chart(
            dept_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.caption(
            "Department rates are descriptive and benchmarked against the "
            "hospital-level rate. Variance is reported in percentage points."
        )



st.divider()

# ---------------------------------------------------------------------------
# Transition intelligence
# ---------------------------------------------------------------------------

st.markdown("## Transition Intelligence")
st.caption(
    "How eligible 30-day readmissions differed from the index encounter. "
    "These patterns are descriptive and do not by themselves indicate causation or avoidability."
)

dept_transition_col, dx_transition_col = st.columns(2, gap="large")


with dept_transition_col:
    st.markdown("### Department Transition")

    if department_transition.empty:
        st.info("No department transition data are available.")
    else:
        dept_transition = department_transition.copy()
        dept_transition["department_transition_pct"] = dept_transition[
            "department_transition_pct"
        ].astype(float)

        dept_transition_fig = go.Figure()

        dept_transition_fig.add_trace(
            go.Bar(
                x=dept_transition["department_transition_pct"],
                y=dept_transition["department_transition"],
                orientation="h",
                text=dept_transition["department_transition_pct"].map(
                    lambda x: f"{x:.2f}%"
                ),
                textposition="outside",
                customdata=dept_transition[
                    ["readmission_count", "total_readmissions"]
                ],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Share: %{x:.2f}%<br>"
                    "Readmissions: %{customdata[0]:,.0f}<br>"
                    "Total eligible readmissions: %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        dept_transition_fig.update_layout(
            height=270,
            margin=dict(l=10, r=45, t=10, b=10),
            showlegend=False,
            xaxis_title="Share of eligible readmissions (%)",
            yaxis_title=None,
            xaxis=dict(
                range=[0, 100],
                ticksuffix="%",
                gridcolor="rgba(15, 23, 42, 0.08)",
            ),
            yaxis=dict(showgrid=False),
        )

        st.plotly_chart(
            dept_transition_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.caption(
            "Same vs different department compares the index-discharge department "
            "with the department of the exact subsequent readmission encounter."
        )


with dx_transition_col:
    st.markdown("### Diagnosis Transition")

    if diagnosis_transition.empty:
        st.info("No diagnosis transition data are available.")
    else:
        dx_transition = diagnosis_transition.copy()
        dx_transition["diagnosis_transition_pct"] = dx_transition[
            "diagnosis_transition_pct"
        ].astype(float)

        dx_transition_fig = go.Figure()

        dx_transition_fig.add_trace(
            go.Bar(
                x=dx_transition["diagnosis_transition_pct"],
                y=dx_transition["diagnosis_transition"],
                orientation="h",
                text=dx_transition["diagnosis_transition_pct"].map(
                    lambda x: f"{x:.2f}%"
                ),
                textposition="outside",
                customdata=dx_transition[
                    ["readmission_count", "total_readmissions"]
                ],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Share: %{x:.2f}%<br>"
                    "Readmissions: %{customdata[0]:,.0f}<br>"
                    "Total eligible readmissions: %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        dx_transition_fig.update_layout(
            height=270,
            margin=dict(l=10, r=45, t=10, b=10),
            showlegend=False,
            xaxis_title="Share of eligible readmissions (%)",
            yaxis_title=None,
            xaxis=dict(
                range=[0, 100],
                ticksuffix="%",
                gridcolor="rgba(15, 23, 42, 0.08)",
            ),
            yaxis=dict(showgrid=False),
        )

        st.plotly_chart(
            dx_transition_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.caption(
            "Same vs different diagnosis compares the recorded index diagnosis "
            "with the diagnosis of the exact subsequent readmission encounter."
        )



st.divider()

# ---------------------------------------------------------------------------
# Patient-level readmission registry
# ---------------------------------------------------------------------------

st.markdown("## Patient-Level Readmission Registry")
st.caption(
    "Drill down from the hospital-level KPI to the eligible readmission events "
    "that make up the numerator. Filters in this section affect the registry only."
)

if registry.empty:
    st.info("No eligible patient-level readmission records are available.")
else:
    registry = registry.copy()

    registry["days_to_readmission"] = registry["days_to_readmission"].astype(int)

    min_days = int(registry["days_to_readmission"].min())
    max_days = int(registry["days_to_readmission"].max())

    department_options = sorted(
        registry["index_department"].dropna().astype(str).unique().tolist()
    )

    with st.expander("Registry filters", expanded=True):
        filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1, 1])

        with filter_col1:
            patient_search = st.text_input(
                "Patient search",
                placeholder="Search patient ID or patient name",
            )

            selected_departments = st.multiselect(
                "Index department",
                options=department_options,
                placeholder="All departments",
            )

        with filter_col2:
            department_transition_filter = st.selectbox(
                "Department transition",
                options=[
                    "All",
                    "Same Department",
                    "Different Department",
                ],
            )

            diagnosis_transition_filter = st.selectbox(
                "Diagnosis transition",
                options=[
                    "All",
                    "Same Diagnosis",
                    "Different Diagnosis",
                ],
            )

        with filter_col3:
            days_range = st.slider(
                "Days to readmission",
                min_value=min_days,
                max_value=max_days,
                value=(min_days, max_days),
            )

            readmission_type_options = sorted(
                registry["readmission_type"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_readmission_types = st.multiselect(
                "Readmission type",
                options=readmission_type_options,
                placeholder="All admission types",
            )

    filtered_registry = registry.copy()

    if patient_search:
        search_term = patient_search.strip()

        patient_match = (
            filtered_registry["patient_name"]
            .astype(str)
            .str.contains(search_term, case=False, na=False)
        )

        id_match = (
            filtered_registry["patient_id"]
            .astype(str)
            .str.contains(search_term, case=False, na=False)
        )

        filtered_registry = filtered_registry[patient_match | id_match]

    if selected_departments:
        filtered_registry = filtered_registry[
            filtered_registry["index_department"].isin(selected_departments)
        ]

    if department_transition_filter != "All":
        filtered_registry = filtered_registry[
            filtered_registry["department_transition"]
            == department_transition_filter
        ]

    if diagnosis_transition_filter != "All":
        filtered_registry = filtered_registry[
            filtered_registry["diagnosis_transition"]
            == diagnosis_transition_filter
        ]

    filtered_registry = filtered_registry[
        filtered_registry["days_to_readmission"].between(
            days_range[0],
            days_range[1],
        )
    ]

    if selected_readmission_types:
        filtered_registry = filtered_registry[
            filtered_registry["readmission_type"].isin(
                selected_readmission_types
            )
        ]

    registry_metric1, registry_metric2, registry_metric3 = st.columns(3)

    with registry_metric1:
        st.metric(
            "Records Shown",
            f"{len(filtered_registry):,}",
        )

    with registry_metric2:
        median_days = (
            filtered_registry["days_to_readmission"].median()
            if not filtered_registry.empty
            else 0
        )
        st.metric(
            "Median Days to Readmission",
            f"{median_days:.0f}",
        )

    with registry_metric3:
        different_department_count = (
            filtered_registry["department_transition"]
            .eq("Different Department")
            .sum()
            if not filtered_registry.empty
            else 0
        )
        st.metric(
            "Different-Department Returns",
            f"{different_department_count:,}",
        )

    display_registry = filtered_registry[
        [
            "patient_id",
            "patient_name",
            "age",
            "gender",
            "city",
            "index_discharge_date",
            "next_admission_date",
            "days_to_readmission",
            "index_department",
            "index_diagnosis",
            "readmission_department",
            "readmission_diagnosis",
            "department_transition",
            "diagnosis_transition",
            "index_admission_type",
            "readmission_type",
            "index_bill_amount",
            "readmission_bill_amount",
        ]
    ].rename(
        columns={
            "patient_id": "Patient ID",
            "patient_name": "Patient",
            "age": "Age",
            "gender": "Gender",
            "city": "City",
            "index_discharge_date": "Index Discharge",
            "next_admission_date": "Readmission Date",
            "days_to_readmission": "Days to Readmission",
            "index_department": "Index Department",
            "index_diagnosis": "Index Diagnosis",
            "readmission_department": "Readmission Department",
            "readmission_diagnosis": "Readmission Diagnosis",
            "department_transition": "Department Transition",
            "diagnosis_transition": "Diagnosis Transition",
            "index_admission_type": "Index Admission Type",
            "readmission_type": "Readmission Type",
            "index_bill_amount": "Index Bill Amount",
            "readmission_bill_amount": "Readmission Bill Amount",
        }
    )

    st.dataframe(
        display_registry,
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "Patient ID": st.column_config.NumberColumn(
                "Patient ID",
                format="%d",
            ),
            "Age": st.column_config.NumberColumn(
                "Age",
                format="%d",
            ),
            "Index Discharge": st.column_config.DateColumn(
                "Index Discharge",
                format="DD MMM YYYY",
            ),
            "Readmission Date": st.column_config.DateColumn(
                "Readmission Date",
                format="DD MMM YYYY",
            ),
            "Days to Readmission": st.column_config.NumberColumn(
                "Days to Readmission",
                format="%d",
            ),
            "Index Bill Amount": st.column_config.NumberColumn(
                "Index Bill Amount",
                format="%.2f",
            ),
            "Readmission Bill Amount": st.column_config.NumberColumn(
                "Readmission Bill Amount",
                format="%.2f",
            ),
        },
    )

    st.download_button(
        label="Download filtered registry (CSV)",
        data=display_registry.to_csv(index=False).encode("utf-8"),
        file_name="careinsights_readmission_registry.csv",
        mime="text/csv",
    )

    st.caption(
        "Synthetic patient records only. This registry contains the eligible "
        "30-day readmission events underlying the hospital KPI; it is not a "
        "production clinical worklist."
    )
