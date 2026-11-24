#!/usr/bin/env bash
# Script pas-à-pas pour créer les ressources GCP et déployer sur Cloud Run (TP Jour 3, slide 71)
set -euo pipefail

# --- À adapter avec votre identifiant de projet GCP ---
export PROJECT_ID="${PROJECT_ID:-mon-projet-gcp-m2}"
export REGION="europe-west1"
export REPO_NAME="dataops-repo"
export SERVICE_NAME="weather-pipeline"
export SA_NAME="sa-weather-pipeline"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export RAW_BUCKET="${PROJECT_ID}-raw-weather"
export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:0.1.0"

# =============================================================================
# ÉTAPE 3 — Créer les ressources GCP (Artifact Registry, GCS, BigQuery, IAM)
# =============================================================================
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker --location="${REGION}" --project="${PROJECT_ID}" || true

gcloud storage buckets create "gs://${RAW_BUCKET}" \
  --location="${REGION}" --uniform-bucket-level-access --project="${PROJECT_ID}" || true

bq --location="${REGION}" mk --dataset "${PROJECT_ID}:weather_trusted__UAT" || true
bq --location="${REGION}" mk --dataset "${PROJECT_ID}:weather_quarantine__UAT" || true

# Service Account dédié (principe du moindre privilège)
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Weather Pipeline Cloud Run" --project="${PROJECT_ID}" || true

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/bigquery.jobUser"
gcloud storage buckets add-iam-policy-binding "gs://${RAW_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectUser"

# =============================================================================
# ÉTAPE 4 — Build, Push & Déploiement Cloud Run sécurisé
# =============================================================================
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# --platform linux/amd64 est indispensable si vous buildez depuis un Mac Apple Silicon
docker build --platform linux/amd64 -t "${IMAGE_URI}" .
docker push "${IMAGE_URI}"

gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --service-account="${SA_EMAIL}" \
  --no-allow-unauthenticated \
  --max-instances=5 --memory=512Mi --cpu=1 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},BQ_DATASET_TRUSTED=weather_trusted__UAT,BQ_DATASET_QUARANTINE=weather_quarantine__UAT,GCS_RAW_BUCKET=${RAW_BUCKET}"

# Test authentifié (Smoke Test HTTPS)
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
curl -fsS -X POST "${SERVICE_URL}/run" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"station_id":"FR-0075","latitude":48.8566,"longitude":2.3522,"partition_ymd":"20270315"}'
