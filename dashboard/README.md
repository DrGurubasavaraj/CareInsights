# Dashboard

The CareInsights dashboard will be built in Streamlit and will consume validated PostgreSQL analytical views rather than reproduce business logic in the UI layer.

Initial Readmissions page:

- KPI cards
- monthly trend
- department comparison
- transition summaries
- diagnosis contribution
- patient-level registry

Database credentials will be supplied locally or through Streamlit secrets and must never be committed.
