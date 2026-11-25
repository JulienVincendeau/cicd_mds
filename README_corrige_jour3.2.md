# Corrigé TP DataOps — Jour 3.2 (Cloud Build + Trigramme `jvi`)

Variante de la Journée 3 qui délègue les tests, le build Docker et le déploiement Cloud Run à **Google Cloud Build** (`cloudbuild.yaml`), en déployant un service isolé par trigramme : **`weather-pipeline-jvi`**.

## Nouveautés par rapport à `jour3`

| Fichier | Rôle |
| :--- | :--- |
| `cloudbuild.yaml` | Pipeline Cloud Build en 4 étapes : **Test** (`ruff` + `pytest`), **Build** Docker, **Push** vers Artifact Registry, puis **Deploy** du service Cloud Run `weather-pipeline-jvi` (paramétrable via `_TRIGRAM`). |
| `deploy.sh` | Prépare Artifact Registry + datasets BigQuery UAT, lance `gcloud builds submit --config=cloudbuild.yaml`, puis vérifie `/health` en HTTPS authentifié. |
| `.dockerignore` | Exclut également `cloudbuild.yaml` de l'image Docker. |

## Déployer en 1 commande avec Cloud Build

```bash
export PROJECT_ID="votre-projet-gcp"

# Déploie weather-pipeline-jvi :
gcloud builds submit --project="${PROJECT_ID}" --config=cloudbuild.yaml .

# (Pour un étudiant avec un autre trigramme, ex: abc -> weather-pipeline-abc)
gcloud builds submit --project="${PROJECT_ID}" --config=cloudbuild.yaml --substitutions=_TRIGRAM=abc .
```

Ou via le script complet (crée aussi Artifact Registry + datasets BigQuery + smoke test `/health`) :
```bash
export PROJECT_ID="votre-projet-gcp"
export TRIGRAM="jvi"
bash deploy.sh
```

> **Note IAM Cloud Build** : le compte de service Cloud Build doit disposer des rôles `roles/run.admin`, `roles/artifactregistry.writer` et `roles/iam.serviceAccountUser` pour déployer sur Cloud Run.
