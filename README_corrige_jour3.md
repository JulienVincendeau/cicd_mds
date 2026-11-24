# Corrigé TP DataOps — Jour 3 (Slide 71)

Assemblage du pipeline qualité dans un micro-service **FastAPI**, conteneurisation **Docker** (`python:3.12-slim` + `uv` + utilisateur non-root) et déploiement sur **Google Cloud Run**.

## Contenu de la branche `jour3`

| Fichier | Rôle dans l'atelier (p. 71) |
| :--- | :--- |
| `src/config.py` | **Étape 1** — Configuration 12-Factor via variables d'environnement (`pydantic-settings`). |
| `src/ingest.py` | **Étape 1** — Client HTTP résilient (`httpx`) vers Open-Meteo avec timeout explicite et backoff exponentiel. |
| `src/load.py` | **Étape 1** — Archivage GCS Raw + chargement BigQuery idempotent (`WRITE_TRUNCATE` sur `$YYYYMMDD`) et table de quarantaine (`WRITE_APPEND`). |
| `src/main.py` | **Étape 1** — API **FastAPI** exposant `GET /health` et `POST /run`. |
| `tests/test_api.py` | Tests rapides de l'API avec `TestClient` et mocks (zéro appel réseau/GCP). |
| `Dockerfile` & `.dockerignore` | **Étape 2** — Image légère `python:3.12-slim-bookworm` + `uv` + utilisateur non-root `appuser` (UID 10001). |
| `deploy.sh` | **Étapes 3 & 4** — Création Artifact Registry, bucket GCS, datasets BigQuery (`__UAT` + `quarantine`), Service Account moindre privilège, build/push et déploiement Cloud Run sécurisé. |

## Tester en local (Python puis Docker)

```bash
# 1. Lint et tests unitaires
uv sync
uv run ruff check .
uv run pytest -v --cov=src

# 2. Build & run Docker en local
docker build -t weather-pipeline:local .
docker run --rm -p 8080:8080 weather-pipeline:local

# 3. Vérifier /health (dans un autre terminal)
curl http://localhost:8080/health
```

## Déployer sur GCP (Étapes 3 & 4)

```bash
export PROJECT_ID="votre-projet-gcp"
bash deploy.sh
```
