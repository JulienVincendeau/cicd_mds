# Dockerfile — Image légère, rapide (uv) et sécurisée (utilisateur non-root) pour Cloud Run
FROM python:3.12-slim-bookworm

# Copie le binaire uv depuis l'image officielle Astral
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/

# Bonnes pratiques Python en conteneur (logs immédiats sur stdout, pas de fichiers .pyc)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 1. Installer les dépendances d'abord (optimise le cache Docker)
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# 2. Copier uniquement le code applicatif
COPY src/ ./src/

# 3. Sécurité : ne JAMAIS exécuter le conteneur en tant que root
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Cloud Run exige d'écouter sur 0.0.0.0 et sur le port défini par PORT (8080 par défaut)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
