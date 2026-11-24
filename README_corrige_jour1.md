# Corrigé TP DataOps — Jour 1 (Slide 32)

Initialisation du socle collaboratif DataOps d'équipe (structure modulaire, `.gitignore`, `pyproject.toml`, Ruff et premiers tests `pytest`).

## Contenu de la branche `jour1`

| Fichier | Rôle dans l'atelier (p. 32) |
| :--- | :--- |
| `.gitignore` | **Étape 1** — Exclut Python (`__pycache__`, `.venv`), fichiers `.env` et clés GCP (`*service-account*.json`). |
| `pyproject.toml` | **Étape 2** — Configuration du projet Python (>=3.12), dépendances dev (`pytest`, `ruff`) et règles Ruff. |
| `src/ingest.py`, `src/contracts.py`, `src/transform.py`, `src/load.py` | **Étape 2** — Arborescence modulaire avec squelettes de fonctions commentés en français. |
| `tests/test_env.py` | **Étape 3** — Premiers tests vérifiant l'environnement Python et les squelettes de fonctions. |

## Lancer les vérifications en local

```bash
uv sync
uv run ruff check .
uv run pytest -v
```

*(Ou avec `pip` : `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]" && ruff check . && pytest -v`)*

## Rappel Étapes 1 & 4 sur GitHub (Gouvernance & PR)

1. Dans **Settings → Branches** sur GitHub, activer une règle de **Branch Protection** sur `main` (Pull Request obligatoire + au moins 1 review).
2. Créer une branche dédiée par ticket : `git switch -c 1-init-skeleton`.
3. Pousser, ouvrir une Pull Request et faire relire par un coéquipier avant de merger sur `main`.
