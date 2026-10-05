-- CareInsights synthetic dataset observation metadata
-- The observation_end_date defines the last date the dataset claims to cover.
-- KPI eligibility should use this field rather than CURRENT_DATE or inferred inactivity.

CREATE TABLE IF NOT EXISTS dataset_metadata (
    dataset_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100),
    observation_start_date DATE,
    observation_end_date DATE,
    source_type VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Current synthetic portfolio dataset.
-- Keep one current metadata row per dataset load/version as appropriate.
INSERT INTO dataset_metadata (
    dataset_name,
    observation_start_date,
    observation_end_date,
    source_type
)
SELECT
    'CareInsights Synthetic Dataset V1',
    DATE '2025-06-22',
    DATE '2026-07-01',
    'Synthetic'
WHERE NOT EXISTS (
    SELECT 1
    FROM dataset_metadata
    WHERE dataset_name = 'CareInsights Synthetic Dataset V1'
      AND observation_start_date = DATE '2025-06-22'
      AND observation_end_date = DATE '2026-07-01'
);
