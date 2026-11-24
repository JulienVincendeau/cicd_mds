"""Module des Data Contracts (Jour 1 : squelette, implémenté en Jour 2)."""


def is_valid_record(record: dict) -> bool:
    """Vérifie qu'un enregistrement contient au moins un identifiant de station."""
    # Sera remplacé par un contrat strict Pydantic v2 en Journée 2
    return bool(record.get("station_id"))
