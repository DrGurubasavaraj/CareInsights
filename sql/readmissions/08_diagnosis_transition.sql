-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Summarize whether patients returned with the same or a different
-- recorded diagnosis during an eligible 30-day readmission.
-- Dependency: vw_readmission_encounter_comparison

CREATE OR REPLACE VIEW vw_readmission_diagnosis_transition AS

WITH diagnosis_transition_registry AS (
    SELECT
        diagnosis_transition,
        COUNT(*) AS readmission_count,
        SUM(COUNT(*)) OVER () AS total_readmissions
    FROM vw_readmission_encounter_comparison
    GROUP BY diagnosis_transition
)

SELECT
    diagnosis_transition,
    readmission_count,
    total_readmissions,
    ROUND(
        100.0 * readmission_count
        / NULLIF(total_readmissions, 0),
        2
    ) AS diagnosis_transition_pct
FROM diagnosis_transition_registry;
