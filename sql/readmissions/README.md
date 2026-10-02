# Readmission SQL Layer

This folder contains the PostgreSQL analytical views used by the CareInsights 30-Day Readmission Intelligence module.

Planned view scripts:

1. `vw_readmission_followup`
2. `vw_readmission_kpi`
3. `vw_readmission_by_department`
4. `vw_readmission_by_diagnosis`
5. `vw_readmission_patient_registry`
6. `vw_readmission_encounter_comparison`
7. `vw_readmission_department_transition`
8. `vw_readmission_diagnosis_transition`
9. `vw_readmission_monthly_trend`

Current synthetic KPI: **119 readmissions / 1,318 eligible index discharges = 9.03%**.

The module separates event-registry logic from denominator-based KPI logic, uses dataset metadata to enforce the 30-day observation window, and validates breakdowns back to the hospital-level KPI.
