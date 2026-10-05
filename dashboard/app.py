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
