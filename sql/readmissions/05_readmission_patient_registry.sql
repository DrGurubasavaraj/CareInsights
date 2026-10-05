-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Create the patient-level registry for eligible 30-day
-- readmission events.
-- Dependencies: patients, dataset_metadata, vw_readmission_followup

CREATE OR REPLACE VIEW vw_readmission_patient_registry AS

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
)

SELECT
    r.patient_id,
    p.patient_name,
    p.age,
    p.gender,
    p.city,
    r.department,
    r.diagnosis,
    r.admission_type,
    r.bill_amount,
    r.discharge_date AS index_discharge_date,
    r.next_admission_date,
    r.days_to_readmission,
    r.next_admission_id
FROM vw_readmission_followup r
JOIN patients p
  ON r.patient_id = p.patient_id
CROSS JOIN current_dataset d
WHERE r.readmission_status = '30-day Readmission'
  AND r.discharge_date IS NOT NULL
  AND r.discharge_date + 30 <= d.observation_end_date;
