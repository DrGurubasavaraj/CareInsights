-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Compare 30-day readmission rates by index-discharge department
-- and benchmark each department against the hospital-level rate.
-- Dependencies: dataset_metadata, vw_readmission_followup, vw_readmission_kpi

CREATE OR REPLACE VIEW vw_readmission_by_department AS

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

department_readmissions AS (
    SELECT
        r.department,

        COUNT(*) FILTER (
            WHERE r.discharge_date IS NOT NULL
              AND r.discharge_date + 30 <= d.observation_end_date
              AND r.readmission_status <> 'Data Review'
        ) AS eligible_discharges,

        COUNT(*) FILTER (
            WHERE r.discharge_date IS NOT NULL
              AND r.discharge_date + 30 <= d.observation_end_date
              AND r.readmission_status = '30-day Readmission'
        ) AS thirty_day_readmissions

    FROM vw_readmission_followup r
    CROSS JOIN current_dataset d
    GROUP BY r.department
),

department_rates AS (
    SELECT
        department,
        eligible_discharges,
        thirty_day_readmissions,
        ROUND(
            100.0 * thirty_day_readmissions
            / NULLIF(eligible_discharges, 0),
            2
        ) AS dept_readmission_pct
    FROM department_readmissions
)

SELECT
    d.department,
    d.eligible_discharges,
    d.thirty_day_readmissions,
    d.dept_readmission_pct,
    k.readmission_rate_pct AS hospital_readmission_pct,
    ROUND(
        d.dept_readmission_pct - k.readmission_rate_pct,
        2
    ) AS variance_from_hospital_pp
FROM department_rates d
CROSS JOIN vw_readmission_kpi k
ORDER BY variance_from_hospital_pp DESC;
