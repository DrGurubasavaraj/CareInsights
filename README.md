# CareInsights

**Healthcare analytics and clinical intelligence platform built with PostgreSQL, Python, and Streamlit.**

CareInsights is a portfolio-grade healthcare analytics project designed to turn hospital encounter data into reusable analytical views, operational KPIs, and patient-level drill-downs. The public repository uses **synthetic data only**.

## Current focus: 30-Day Readmission Intelligence

The first analytical module implements a reusable 30-day readmission data mart in PostgreSQL with:

- observation-window metadata
- index-discharge eligibility logic
- 30-day readmission KPI calculation
- department and diagnosis breakdowns
- patient-level readmission registry
- index-vs-readmission encounter comparison
- department and diagnosis transition analysis
- monthly readmission trend with partial-month safeguards

### Current synthetic KPI

- **Eligible index discharges:** 1,318
- **30-day readmissions:** 119
- **30-day readmission rate:** 9.03%

These are project metrics from a synthetic dataset, not a formally validated production hospital quality measure.

## Architecture

```text
Synthetic hospital data
        |
        v
PostgreSQL
        |
        v
Validated analytical views
        |
        v
Python / Streamlit
        |
        v
CareInsights dashboard
```

## Repository structure

```text
CareInsights/
├── database/
├── sql/
│   └── readmissions/
├── dashboard/
├── .streamlit/
├── .gitignore
├── requirements.txt
└── README.md
```

## Technology stack

- PostgreSQL
- Python
- Streamlit
- pandas
- Plotly
- SQLAlchemy / psycopg2

## Data safety

This repository is intended for **synthetic or properly de-identified data only**. Real patient-identifiable hospital data, database passwords, API keys, connection strings, and Streamlit secrets must never be committed.

A future hospital pilot should remain separate from the public portfolio repository and use approved private infrastructure and governance.

## Planned dashboard

The Readmissions page will follow an executive-to-drill-down workflow:

1. hospital-level KPI cards
2. monthly readmission trend
3. department comparison
4. department and diagnosis transition patterns
5. diagnosis contribution analysis
6. patient-level readmission registry

## Status

- **Backend analytical layer:** validated for the synthetic portfolio dataset
- **Repository scaffold:** initialized
- **Streamlit UI:** next milestone
