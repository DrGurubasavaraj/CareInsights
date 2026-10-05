# CareInsights

**Healthcare analytics and clinical intelligence platform built with PostgreSQL, Python, Streamlit, and a managed cloud database.**

CareInsights is a portfolio-grade healthcare analytics project designed to turn hospital encounter data into reusable analytical views, operational KPIs, trend analysis, and patient-level drill-downs.

> **Live app:** https://careinsights.streamlit.app/

The public deployment uses **synthetic data only**.

## V1.0 — 30-Day Readmission Intelligence

The first deployed module implements a reusable 30-day readmission analytics layer in PostgreSQL and exposes it through an interactive Streamlit dashboard.

### Current validated synthetic KPI

- **Eligible index discharges:** 1,318
- **30-day readmissions:** 119
- **30-day readmission rate:** 9.03%
- **Different-department readmissions:** 96
- **Patient-level registry rows:** 119

These are project metrics from a synthetic dataset. They are **not** presented as a formally validated production hospital quality measure.

## What the dashboard includes

### Executive KPI layer
- 30-day readmission rate
- eligible index discharges
- 30-day readmission count
- dataset observation cutoff

### Monthly trend
- readmission rate by index-discharge month
- complete-month cohort logic
- partial boundary-month safeguards
- hospital-level benchmark line

### Department comparison
- eligible discharges by department
- department-level readmission rates
- hospital benchmark
- variance from hospital rate in percentage points

### Transition intelligence
- same vs different department on readmission
- same vs different recorded diagnosis on readmission

### Patient-level readmission registry
- patient search
- index-department filtering
- department-transition filtering
- diagnosis-transition filtering
- days-to-readmission filtering
- readmission-type filtering
- encounter-level index vs readmission comparison
- downloadable filtered CSV

## Architecture

```text
Synthetic hospital data
        |
        v
PostgreSQL analytical layer
        |
        v
Validated SQL views
        |
        v
SQLAlchemy / psycopg
        |
        v
Streamlit application
        |
        v
CareInsights dashboard
```

### Deployment architecture

```text
GitHub
  |
  v
Streamlit Community Cloud
  |
  v
Managed PostgreSQL (Neon)
  |
  v
CareInsights analytical views + synthetic data
```

The application code and SQL definitions are version-controlled in GitHub. Operational data remains in PostgreSQL rather than being embedded in the public repository.

## Readmission SQL layer

The PostgreSQL analytical layer currently includes:

1. `vw_readmission_followup`
2. `vw_readmission_kpi`
3. `vw_readmission_by_department`
4. `vw_readmission_by_diagnosis`
5. `vw_readmission_patient_registry`
6. `vw_readmission_encounter_comparison`
7. `vw_readmission_department_transition`
8. `vw_readmission_diagnosis_transition`
9. `vw_readmission_monthly_trend`

Key analytical safeguards include:

- complete 30-day observation-window eligibility
- separation of event-registry logic from KPI denominator logic
- exclusion of `Data Review` records from the KPI denominator
- stable `admission_id` keys for encounter matching
- reconciliation of patient-level outputs back to the hospital-level KPI
- complete vs partial calendar-month classification
- null-safe comparison of index and readmission encounter attributes

## Repository structure

```text
CareInsights/
├── database/
│   └── dataset_metadata.sql
├── sql/
│   └── readmissions/
│       ├── 01_readmission_followup.sql
│       ├── 02_readmission_kpi.sql
│       ├── 03_readmission_by_department.sql
│       ├── 04_readmission_by_diagnosis.sql
│       ├── 05_readmission_patient_registry.sql
│       ├── 06_readmission_encounter_comparison.sql
│       ├── 07_department_transition.sql
│       ├── 08_diagnosis_transition.sql
│       └── 09_monthly_trend.sql
├── dashboard/
│   ├── app.py
│   └── db.py
├── .streamlit/
├── .gitignore
├── requirements.txt
└── README.md
```

## Technology stack

- PostgreSQL 18
- Python
- Streamlit
- pandas
- Plotly
- SQLAlchemy
- psycopg / psycopg2
- Neon PostgreSQL
- GitHub
- Streamlit Community Cloud

## Local development

Create a local Streamlit secrets file from the provided example:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then configure your local PostgreSQL connection in `.streamlit/secrets.toml`.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run dashboard/app.py
```

## Data safety and clinical-use boundary

This repository is intended for **synthetic or appropriately de-identified data only**.

Do not commit:

- real patient-identifiable hospital data
- database passwords
- API keys
- connection strings
- Streamlit secrets
- private hospital extracts

A real hospital pilot should use an approved private data environment, access controls, governance, and an explicitly defined clinical/operational use case before any production use.

## Pilot direction

The next phase is to evaluate CareInsights as a hospital pilot using an approved data feed from the hospital EMR or another governed source.

The intended architecture is:

```text
Hospital EMR / approved extract / API
        |
        v
Governed PostgreSQL analytics layer
        |
        v
CareInsights analytical views
        |
        v
Private dashboard for authorized users
```

The public synthetic deployment is intended to validate the analytical workflow and application architecture before any real-data pilot.

## Status

- **Readmission analytical layer:** deployed
- **Cloud PostgreSQL backend:** deployed
- **Streamlit dashboard:** live
- **Patient-level drill-down:** live
- **Hospital pilot:** planning stage

## Live demo

**CareInsights:** https://careinsights.streamlit.app/
