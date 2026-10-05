-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Show diagnosis concentration among eligible readmissions for
-- departments whose readmission rate is above the hospital rate.
-- Dependencies: dataset_metadata, vw_readmission_followup,
--               vw_readmission_by_department

CREATE OR REPLACE VIEW vw_readmission_by_diagnosis AS

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

diagnosis_readmissions AS (
    SELECT
        r.department,
        r.diagnosis,
        COUNT(*) AS readmission_count,
        SUM(COUNT(*)) OVER (
            PARTITION BY r.department
        ) AS dept_total_readmissions

    FROM vw_readmission_followup r
    JOIN vw_readmission_by_department d
      ON r.department = d.department
    CROSS JOIN current_dataset c

    WHERE d.variance_from_hospital_pp > 0
      AND r.readmission_status = '30-day Readmission'
      AND r.discharge_date IS NOT NULL
      AND r.discharge_date + 30 <= c.observation_end_date

    GROUP BY
        r.department,
        r.diagnosis
)

SELECT
    department,
    diagnosis,
    readmission_count,
    dept_total_readmissions,
    ROUND(
        100.0 * readmission_count
        / NULLIF(dept_total_readmissions, 0),
        2
    ) AS diagnosis_share_pct
FROM diagnosis_readmissions
ORDER BY
    department,
    diagnosis_share_pct DESC;
