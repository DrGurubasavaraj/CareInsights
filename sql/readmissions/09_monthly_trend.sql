-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Calculate monthly readmission rates by index-discharge month and
-- flag incomplete boundary months so dashboard trends can default to complete
-- calendar-month cohorts.
-- Dependencies: dataset_metadata, vw_readmission_followup

CREATE OR REPLACE VIEW vw_readmission_monthly_trend AS

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

monthly_readmissions AS (
    SELECT
        DATE_TRUNC(
            'month',
            r.discharge_date::timestamp with time zone
        )::date AS discharge_month,

        COUNT(*) AS eligible_discharges,

        COUNT(*) FILTER (
            WHERE r.readmission_status = '30-day Readmission'
        ) AS thirty_day_readmissions,

        d.observation_start_date,
        d.observation_end_date

    FROM vw_readmission_followup r
    CROSS JOIN current_dataset d

    WHERE r.discharge_date IS NOT NULL
      AND r.discharge_date + 30 <= d.observation_end_date
      AND r.readmission_status <> 'Data Review'

    GROUP BY
        DATE_TRUNC(
            'month',
            r.discharge_date::timestamp with time zone
        )::date,
        d.observation_start_date,
        d.observation_end_date
)

SELECT
    discharge_month,
    eligible_discharges,
    thirty_day_readmissions,

    ROUND(
        100.0 * thirty_day_readmissions
        / NULLIF(eligible_discharges, 0),
        2
    ) AS monthly_readmission_pct,

    observation_start_date,
    observation_end_date,

    CASE
        WHEN observation_start_date > discharge_month
            THEN 'Partial Month'

        WHEN (
            discharge_month
            + INTERVAL '1 month'
            - INTERVAL '1 day'
            + INTERVAL '30 days'
        )::date > observation_end_date
            THEN 'Partial Month'

        ELSE 'Complete Month'
    END AS month_completeness

FROM monthly_readmissions
ORDER BY discharge_month;
