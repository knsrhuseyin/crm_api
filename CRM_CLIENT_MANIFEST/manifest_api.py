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
from CRM_CLIENT_MANIFEST.manifest_generator import update_manifest_cache

manifest_router = APIRouter(prefix="/update", tags=["Update Client Version"])


# =======================
# Endpoint API
# =======================
@manifest_router.get("/latest")
def latest_update() -> dict:
    """Récupère le manifest de la dernière version du client.

    Le manifest inclut la version, l'URL de base et les hash SHA256 de chaque fichier.
    Il est mis en cache et recalculé uniquement si le contenu du dossier client change.

    Returns:
        dict: Manifest complet, prêt pour le téléchargement sélectif côté client.
    """
    return update_manifest_cache()
