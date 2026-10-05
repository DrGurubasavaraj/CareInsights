-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Calculate the hospital-level 30-day readmission KPI using
-- only index discharges with a complete 30-day observation window.
-- Dependencies: dataset_metadata, vw_readmission_followup

CREATE OR REPLACE VIEW vw_readmission_kpi AS

WITH current_dataset AS (
    SELECT
        dataset_id,
        dataset_name,
        observation_start_date,
        observation_end_date,
        source_type,
        loaded_at
    FROM dataset_metadata
    ORDER BY dataset_id DESC
    LIMIT 1
),

readmission_kpi AS (
    SELECT
        COUNT(*) FILTER (
            WHERE r.discharge_date IS NOT NULL
              AND r.discharge_date + 30 <= d.observation_end_date
              AND r.readmission_status = '30-day Readmission'
        ) AS thirty_day_readmissions,

        COUNT(*) FILTER (
            WHERE r.discharge_date IS NOT NULL
              AND r.discharge_date + 30 <= d.observation_end_date
              AND r.readmission_status <> 'Data Review'
        ) AS total_eligible_discharges

    FROM vw_readmission_followup r
    CROSS JOIN current_dataset d
)

SELECT
    thirty_day_readmissions,
    total_eligible_discharges,
    ROUND(
        100.0 * thirty_day_readmissions
        / NULLIF(total_eligible_discharges, 0),
        2
    ) AS readmission_rate_pct
FROM readmission_kpi;
