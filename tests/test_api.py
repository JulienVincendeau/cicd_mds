"""Tests unitaires de l'API FastAPI (Jour 3) — sans appel réseau ni GCP réel."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """L'endpoint /health doit répondre 200 OK avec {"status": "ok"}."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_run_endpoint_separe_valides_et_quarantaine(monkeypatch):
    """Vérifie POST /run de bout en bout en mockant l'API Open-Meteo (mode local)."""
    # Réponse Open-Meteo simulée : 1 mesure saine + 1 mesure aberrante (+999 °C)
    fausse_reponse = {
        "hourly": {
            "time": ["2027-03-10T10:00", "2027-03-10T11:00"],
            "temperature_2m": [18.5, 999.0],
            "relative_humidity_2m": [60.0, 55.0],
        }
    }
    monkeypatch.setattr("src.main.fetch_city_weather", lambda lat, lon: fausse_reponse)

    resp = client.post(
        "/run",
        json={
            "station_id": "FR-0075",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "partition_ymd": "20270310",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["station_id"] == "FR-0075"
    assert body["loaded"] == 1
    assert body["quarantined"] == 1
    assert "run_id" in body


def test_run_endpoint_rejette_payload_invalide():
    """Un payload avec une date de partition mal formée renvoie HTTP 422."""
    resp = client.post(
        "/run",
        json={"station_id": "PARIS", "partition_ymd": "2027-03-10"},
    )
    assert resp.status_code == 422
