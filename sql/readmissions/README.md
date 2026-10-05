# Readmission SQL Layer

This folder contains the PostgreSQL analytical views used by the CareInsights **30-Day Readmission Intelligence** module.

## Implemented views

Run the scripts in numerical order:

1. `01_readmission_followup.sql` → `vw_readmission_followup`
2. `02_readmission_kpi.sql` → `vw_readmission_kpi`
3. `03_readmission_by_department.sql` → `vw_readmission_by_department`
4. `04_readmission_by_diagnosis.sql` → `vw_readmission_by_diagnosis`
5. `05_readmission_patient_registry.sql` → `vw_readmission_patient_registry`
6. `06_readmission_encounter_comparison.sql` → `vw_readmission_encounter_comparison`
7. `07_department_transition.sql` → `vw_readmission_department_transition`
8. `08_diagnosis_transition.sql` → `vw_readmission_diagnosis_transition`
9. `09_monthly_trend.sql` → `vw_readmission_monthly_trend`

## Current validated synthetic KPI

- **30-day readmissions:** 119
- **Eligible index discharges:** 1,318
- **30-day readmission rate:** 9.03%

The module separates the event registry from the denominator-based KPI cohort, uses `dataset_metadata.observation_end_date` to enforce a complete 30-day follow-up window, and reconciles department and patient-level outputs back to the hospital-level KPI.

## Analytical safeguards

- Stable `admission_id` keys are used for encounter matching.
- `Data Review` records are excluded from the KPI denominator.
- Monthly trends distinguish complete from partial calendar months.
- Department variance is reported in percentage points relative to the hospital rate.
- Diagnosis and department transition outputs are descriptive, not causal quality judgments.

## Data safety

Only synthetic or appropriately de-identified data belongs in the public repository.
