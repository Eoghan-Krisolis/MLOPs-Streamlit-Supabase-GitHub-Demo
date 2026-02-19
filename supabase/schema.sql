-- ==========================================
-- TABLE: predictions
-- ==========================================
create table if not exists predictions (
  id bigserial primary key,

  request_id text not null unique,
  ts timestamptz not null,
  model_version text not null,

  -- ---------
  -- Features (match your training dataset column names)
  -- ---------
  "Age" double precision not null,
  "MotorValue" double precision not null,
  "HealthDependentsAdults" double precision not null,
  "HealthDependentsKids" double precision not null,

  "CreditCardType" text not null,
  "MotorType" text not null,
  "HealthType" text not null,
  "TravelType" text not null,

  -- Binary values stored RAW (not 0/1)
  "MotorInsurance" text not null,
  "HealthInsurance" text not null,
  "TravelInsurance" text not null,

  "Gender" text not null,
  "Location" text not null,

  -- ---------
  -- Model outputs (3-class)
  -- ---------
  predicted_label text not null,
  proba_email double precision,
  proba_phone double precision,
  proba_sms double precision
);

create index if not exists idx_predictions_ts on predictions(ts);


-- ==========================================
-- TABLE: monitoring_metrics
-- ==========================================
create table if not exists monitoring_metrics (
  id bigserial primary key,

  ts timestamptz not null,
  model_version text not null,

  window_days integer not null,
  current_rows integer not null,

  drift_share double precision not null,
  drifted_features jsonb not null,

  threshold double precision not null,
  retrain_triggered boolean not null
);

create index if not exists idx_monitoring_metrics_ts on monitoring_metrics(ts);


-- ==========================================
-- RLS (recommended)
-- ==========================================

-- Predictions: allow Streamlit (anon) to insert only
alter table predictions enable row level security;

create policy "anon can insert predictions"
on predictions
for insert
to anon
with check (true);

create policy "service role can read predictions"
on predictions
for select
to service_role
using (true);


-- Monitoring metrics: service role only
alter table monitoring_metrics enable row level security;

create policy "service role can insert monitoring metrics"
on monitoring_metrics
for insert
to service_role
with check (true);

create policy "service role can read monitoring metrics"
on monitoring_metrics
for select
to service_role
using (true);
