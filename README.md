# TP DataOps & CI/CD sur Google Cloud (M2 Data)

Ce dépôt contient les corrigés progressifs des ateliers pratiques guidés, organisés avec **une branche par journée** :

- **`jour1`** (slide 32) : Initialisation du dépôt DataOps, structure modulaire, `.gitignore`, `pyproject.toml`, Ruff et premier test `pytest`.
- **`jour2`** (slide 56) : Data Contract **Pydantic v2**, normalisation (trim, UTC), Quarantaine (DLQ), déduplication et suite `pytest` + test SQL **DuckDB**.
- **`jour3`** (slide 71) : Assemblage du pipeline derrière **FastAPI** (`/health`, `/run`), configuration 12-Factor, **Dockerfile** (`python:3.12-slim` + `uv` + utilisateur non-root) et déploiement **Cloud Run**.

## Naviguer entre les corrigés

```bash
git checkout jour1   # Corrigé Journée 1
git checkout jour2   # Corrigé Journée 2
git checkout jour3   # Corrigé Journée 3
```
