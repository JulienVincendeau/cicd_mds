"""Test de vérification de l'environnement Python."""

import sys


def test_python_version_minimum():
    """Vérifie que l'environnement utilise bien Python 3.12 ou supérieur."""
    assert sys.version_info >= (3, 12)
