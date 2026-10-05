-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Summarize whether patients returned to the same or a different
-- department during an eligible 30-day readmission.
-- Dependency: vw_readmission_encounter_comparison

CREATE OR REPLACE VIEW vw_readmission_department_transition AS

WITH dept_transition_registry AS (
    SELECT
        department_transition,
        COUNT(*) AS readmission_count,
        SUM(COUNT(*)) OVER () AS total_readmissions
    FROM vw_readmission_encounter_comparison
    GROUP BY department_transition
)

SELECT
    department_transition,
    readmission_count,
    total_readmissions,
    ROUND(
        100.0 * readmission_count
        / NULLIF(total_readmissions, 0),
        2
    ) AS department_transition_pct
FROM dept_transition_registry;
