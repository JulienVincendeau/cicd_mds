"""Ingestion HTTP résiliente depuis l'API Open-Meteo (timeouts + retries)."""

import logging
import time

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


def fetch_city_weather(lat: float, lon: float, max_retries: int = 3) -> dict:
    """Appelle l'API Open-Meteo avec timeout explicite et backoff exponentiel (2s, 4s...)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "UTC",
        "forecast_days": 1,
    }

    for attempt in range(1, max_retries + 1):
        try:
            # Toujours définir un timeout explicite sur un appel réseau externe
            with httpx.Client(timeout=settings.http_timeout_sec) as client:
                response = client.get(settings.source_api_url, params=params)
                response.raise_for_status()
                return response.json()
        except (httpx.TimeoutException, httpx.HTTPStatusError):
            if attempt == max_retries:
                logger.error("Échec d'ingestion API après %s tentatives", attempt)
                raise
            # Backoff exponentiel pour éviter de surcharger l'API partenaire
            attente = 2**attempt
            logger.warning("Erreur HTTP transitoire, nouvelle tentative dans %ss", attente)
            time.sleep(attente)

    return {}  # pragma: no cover


def parse_open_meteo_payload(payload: dict, station_id: str) -> list[dict]:
    """Convertit la réponse JSON horaire d'Open-Meteo en liste d'observations brutes."""
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])

    records: list[dict] = []
    for obs_time, temp, hum in zip(times, temps, humidities, strict=False):
        # Open-Meteo renvoie des dates UTC sans suffixe 'Z' : on le rend explicite
        iso_utc = obs_time if obs_time.endswith("Z") else f"{obs_time}Z"
        records.append(
            {
                "station_id": station_id,
                "observed_at": iso_utc,
                "temperature_c": temp,
                "humidity_pct": hum,
            }
        )
    return records
