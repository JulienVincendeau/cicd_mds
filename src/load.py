"""Chargement idempotent dans BigQuery (Trusted par partition + Quarantaine)."""

import json
import logging
from datetime import UTC, datetime

from google.cloud import bigquery, storage

from src.config import settings

logger = logging.getLogger(__name__)

# Schéma explicite BigQuery (jamais d'autodetect en production !)
TRUSTED_SCHEMA = [
    bigquery.SchemaField("station_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("observed_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("temperature_c", "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("humidity_pct", "FLOAT64", mode="REQUIRED"),
]

QUARANTINE_SCHEMA = [
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("reason", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("raw_payload", "STRING", mode="REQUIRED"),
]


def save_raw_to_gcs(payload: dict, run_id: str, partition_ymd: str) -> str | None:
    """Archive le JSON brut dans Cloud Storage (couche Raw immuable)."""
    if not settings.gcs_raw_bucket or settings.gcp_project_id == "local":
        logger.info("Archivage GCS ignoré (mode local ou bucket non configuré)")
        return None

    client = storage.Client(project=settings.gcp_project_id)
    bucket = client.bucket(settings.gcs_raw_bucket)
    blob_path = f"raw/weather/{partition_ymd}/{run_id}.json"
    bucket.blob(blob_path).upload_from_string(json.dumps(payload), content_type="application/json")
    return f"gs://{settings.gcs_raw_bucket}/{blob_path}"


def load_partition_idempotent(rows: list[dict], partition_ymd: str) -> int:
    """Charge les lignes valides en WRITE_TRUNCATE sur la partition du jour ($YYYYMMDD).

    Relancer ce job 2 ou 10 fois pour le même jour produit exactement le même résultat.
    """
    if not rows:
        return 0

    if settings.gcp_project_id == "local":
        logger.info("Mode local : %s lignes valides prêtes pour BigQuery", len(rows))
        return len(rows)

    client = bigquery.Client(project=settings.gcp_project_id)
    table_id = (
        f"{settings.gcp_project_id}.{settings.bq_dataset_trusted}.observations${partition_ymd}"
    )
    job_config = bigquery.LoadJobConfig(
        schema=TRUSTED_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(field="observed_at"),
    )
    client.load_table_from_json(rows, table_id, job_config=job_config).result()
    return len(rows)


def append_quarantine(bad_rows: list[dict], run_id: str) -> int:
    """Enregistre les lignes rejetées en WRITE_APPEND dans la table de quarantaine."""
    if not bad_rows:
        return 0

    if settings.gcp_project_id == "local":
        logger.info("Mode local : %s lignes envoyées en quarantaine", len(bad_rows))
        return len(bad_rows)

    now_iso = datetime.now(UTC).isoformat()
    payload_rows = [
        {
            "run_id": run_id,
            "ingested_at": now_iso,
            "reason": item["reason"],
            "raw_payload": json.dumps(item["raw"], default=str),
        }
        for item in bad_rows
    ]

    client = bigquery.Client(project=settings.gcp_project_id)
    table_id = f"{settings.gcp_project_id}.{settings.bq_dataset_quarantine}.weather_errors"
    job_config = bigquery.LoadJobConfig(
        schema=QUARANTINE_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json(payload_rows, table_id, job_config=job_config).result()
    return len(payload_rows)
