-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Compare each eligible index encounter with its exact readmission
-- encounter using the stable next_admission_id key.
-- Dependencies: admissions, vw_readmission_patient_registry

CREATE OR REPLACE VIEW vw_readmission_encounter_comparison AS

SELECT
    r.patient_id,
    r.patient_name,
    r.index_discharge_date,
    r.next_admission_date,
    r.days_to_readmission,
    r.next_admission_id,

    r.department AS index_department,
    r.diagnosis AS index_diagnosis,

    a.admission_id AS readmission_admission_id,
    a.department AS readmission_department,
    a.diagnosis AS readmission_diagnosis,

    CASE
        WHEN r.department IS NOT DISTINCT FROM a.department
            THEN 'Same Department'
        ELSE 'Different Department'
    END AS department_transition,

    CASE
        WHEN r.diagnosis IS NOT DISTINCT FROM a.diagnosis
            THEN 'Same Diagnosis'
        ELSE 'Different Diagnosis'
    END AS diagnosis_transition,

    a.admission_type AS readmission_type,
    a.bill_amount AS readmission_bill_amount

FROM vw_readmission_patient_registry r
JOIN admissions a
  ON r.next_admission_id = a.admission_id
 AND r.patient_id = a.patient_id;
