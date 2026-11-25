"""Point d'entrée FastAPI du micro-service DataOps (Cloud Run).

Expose deux endpoints :
- GET  /health : sonde de santé vérifiée par Cloud Run et en test local.
- POST /run    : exécute le pipeline complet (ingest -> contracts/transform -> load).
"""

import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.ingest import fetch_city_weather, parse_open_meteo_payload
from src.load import append_quarantine, load_partition_idempotent, save_raw_to_gcs
from src.transform import split_valid_and_quarantine

app = FastAPI(title="Weather Quality Micro-Pipeline")


class TriggerPayload(BaseModel):
    """Paramètres attendus lors d'un appel POST /run (Scheduler, Pub/Sub ou curl)."""

    station_id: str = Field(default="FR-0075", pattern=r"^FR-[0-9]{4}$")
    latitude: float = 48.8566
    longitude: float = 2.3522
    partition_ymd: str = Field(pattern=r"^[0-9]{8}$")


@app.get("/health")
def health() -> dict:
    """Endpoint léger utilisé pour vérifier que le conteneur répond."""
    return {"status": "ok"}


@app.post("/run")
def run_pipeline(req: TriggerPayload) -> dict:
    """Exécute une passe complète du pipeline de qualité météo."""
    run_id = str(uuid.uuid4())

    # 1. Ingestion depuis l'API OpenData + archivage brut sur GCS
    raw_payload = fetch_city_weather(req.latitude, req.longitude)
    save_raw_to_gcs(raw_payload, run_id=run_id, partition_ymd=req.partition_ymd)

    # 2. Mise à plat + validation contrat Pydantic + séparation Quarantaine
    records = parse_open_meteo_payload(raw_payload, station_id=req.station_id)
    valid_rows, bad_rows = split_valid_and_quarantine(records)

    # 3. Chargement idempotent BigQuery (Trusted) + log des rejets (Quarantaine)
    loaded = load_partition_idempotent(valid_rows, partition_ymd=req.partition_ymd)
    quarantined = append_quarantine(bad_rows, run_id=run_id)

    return {
        "run_id": run_id,
        "station_id": req.station_id,
        "loaded": loaded,
        "quarantined": quarantined,
    }
