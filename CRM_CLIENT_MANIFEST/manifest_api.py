"""
server_update_api.py
====================

Module FastAPI pour la gestion du manifest de mise à jour du CRM client.

Ce module fournit un endpoint `/update/latest` qui retourne les informations de la
dernière version du client, ainsi que les hash SHA256 de chaque fichier pour permettre
le téléchargement sélectif côté client. Le manifest est mis en cache et recalculé uniquement
si le contenu du dossier client change.


Dependencies:
    fastapi, pathlib, hashlib, json, threading, typing

"""

from fastapi import APIRouter

import threading
from typing import Dict

from CRM_CLIENT_MANIFEST.manifest_generator import update_manifest_cache

manifest_router = APIRouter(prefix="/update", tags=['Update Client Version'])


# =======================
# Endpoint API
# =======================
@manifest_router.get("/latest")
def latest_update():
    """Endpoint pour récupérer le manifest du client.

    Retourne le manifest complet, incluant la version, l'URL de base et les hash
    SHA256 de chaque fichier.

    Le manifest est mis en cache et recalculé uniquement si nécessaire.

    Returns:
        dict: Manifest complet prêt à être utilisé par le client pour le téléchargement
              sélectif.
    """
    return update_manifest_cache()
