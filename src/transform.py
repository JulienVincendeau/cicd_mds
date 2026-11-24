"""Module de transformation et nettoyage (Jour 1 : squelette, enrichi en Jour 2)."""


def normalize_station_id(station_id: str) -> str:
    """Supprime les espaces superflus et met le code station en majuscules."""
    return station_id.strip().upper()
