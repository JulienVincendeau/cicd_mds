"""Premiers tests unitaires (Jour 1) : vérification de l'environnement et du squelette."""

import sys

from src.contracts import is_valid_record
from src.ingest import fetch_raw_data
from src.load import load_records
from src.transform import normalize_station_id


def test_python_version_minimum():
    """Vérifie que l'environnement utilise bien Python 3.12 ou supérieur."""
    assert sys.version_info >= (3, 12)


def test_normalize_station_id():
    """Vérifie que le squelette de transformation nettoie espaces et casse."""
    assert normalize_station_id("  fr-0075  ") == "FR-0075"


def test_pipeline_skeleton_modules():
    """Vérifie que tous les modules du squelette répondent correctement."""
    assert fetch_raw_data() == []
    assert is_valid_record({"station_id": "FR-0075"}) is True
    assert is_valid_record({}) is False
    assert load_records([{"station_id": "FR-0075"}]) == 1
