#!/usr/bin/env bash
# Script TP Jour 3.2 : prépare les ressources GCP et déploie weather-pipeline-jvi via Cloud Build
set -euo pipefail

# --- À adapter avec votre projet GCP et votre trigramme (par défaut : jvi) ---
export PROJECT_ID="${PROJECT_ID:-mon-projet-gcp-m2}"
export TRIGRAM="${TRIGRAM:-jvi}"
export REGION="europe-west1"
export REPO_NAME="dataops-repo"
export SERVICE_NAME="weather-pipeline-${TRIGRAM}"

# 1. Créer le dépôt Artifact Registry et les datasets BigQuery UAT (si absents)
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker --location="${REGION}" --project="${PROJECT_ID}" || true

bq --location="${REGION}" mk --dataset "${PROJECT_ID}:weather_trusted__UAT" || true
bq --location="${REGION}" mk --dataset "${PROJECT_ID}:weather_quarantine__UAT" || true

# 2. Lancer le pipeline Cloud Build (Tests -> Docker Build -> Push -> Cloud Run Deploy)
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --config=cloudbuild.yaml \
  --substitutions="_TRIGRAM=${TRIGRAM},_REGION=${REGION},_AR_REPO=${REPO_NAME}" \
  .

# 3. Smoke Test HTTPS authentifié sur le service déployé (weather-pipeline-jvi)
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

echo "Service déployé : ${SERVICE_URL}"
curl -fsS -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  "${SERVICE_URL}/health"
echo ""
