-- CareInsights: 30-Day Readmission Intelligence
-- Purpose: Sequence admissions per patient and derive the next encounter,
-- days to readmission, and event-level readmission status.
-- Source tables: admissions

CREATE OR REPLACE VIEW vw_readmission_followup AS

WITH discharge_followup AS (
    SELECT
        a.patient_id,
        a.admission_id,
        a.admission_date,
        a.discharge_date,
        LEAD(a.admission_date) OVER (
            PARTITION BY a.patient_id
            ORDER BY a.admission_date, a.admission_id
        ) AS next_admission_date,
        LEAD(a.admission_id) OVER (
            PARTITION BY a.patient_id
            ORDER BY a.admission_date, a.admission_id
        ) AS next_admission_id,
        a.department,
        a.diagnosis,
        a.admission_type,
        a.bill_amount
    FROM admissions a
),

readmission_followup AS (
    SELECT
        d.patient_id,
        d.admission_id,
        d.admission_date,
        d.discharge_date,
        d.next_admission_date,
        d.next_admission_date - d.discharge_date AS days_to_readmission,
        CASE
            WHEN d.discharge_date IS NULL
                THEN 'Still Admitted / Data Review'
            WHEN d.next_admission_date IS NULL
                THEN 'No Subsequent Admission'
            WHEN d.next_admission_date - d.discharge_date <= 0
                THEN 'Data Review'
            WHEN d.next_admission_date - d.discharge_date <= 30
                THEN '30-day Readmission'
            ELSE 'No 30-day Readmission'
        END AS readmission_status,
        d.diagnosis,
        d.department,
        d.admission_type,
        d.bill_amount,
        d.next_admission_id
    FROM discharge_followup d
)

SELECT
    patient_id,
    admission_id,
    admission_date,
    discharge_date,
    next_admission_date,
    days_to_readmission,
    readmission_status,
    diagnosis,
    department,
    admission_type,
    bill_amount,
    next_admission_id
FROM readmission_followup;
