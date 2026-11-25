"""Configuration 12-Factor : toutes les variables d'environnement viennent de l'extérieur.

La même image Docker tourne ainsi en local, en UAT et en Production :
seules les variables d'environnement injectées par Cloud Run changent.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    """Paramètres du pipeline injectés via variables d'environnement ou fichier .env."""

    # Projet GCP cible ("local" permet de tester le service sans compte GCP)
    gcp_project_id: str = "local"
    # Datasets BigQuery isolés par environnement (__TST, __UAT ou Prod)
    bq_dataset_trusted: str = "weather_trusted__UAT"
    bq_dataset_quarantine: str = "weather_quarantine__UAT"
    # Bucket Cloud Storage pour archiver la donnée brute (optionnel en local)
    gcs_raw_bucket: str = ""
    # API OpenData météo et timeout réseau explicite (en secondes)
    source_api_url: str = "https://api.open-meteo.com/v1/forecast"
    http_timeout_sec: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = PipelineSettings()
