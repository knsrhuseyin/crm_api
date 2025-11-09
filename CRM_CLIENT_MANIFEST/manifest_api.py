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
from pathlib import Path
import hashlib
import json
import threading
from typing import Dict

from env_var import CLIENT_DIR, VERSION, DOWNLOAD_URL

manifest_router = APIRouter(prefix="/update", tags=['Update Client Version'])

# =======================
# Configuration
# =======================
CLIENT_DIR = Path(f"{CLIENT_DIR}/crm-client")
VERSION = VERSION
BASE_URL = DOWNLOAD_URL
CACHE_FILE = Path(f"{CLIENT_DIR}/manifest_cache.json")

# =======================
# Variables cache
# =======================
manifest_cache: Dict = {}
LAST_MOD = 0
CACHE_LOCK = threading.Lock()

# =======================
# Fonctions utilitaires
# =======================
def sha256_file(file_path: Path) -> str:
    """Calcule le hash SHA256 d'un fichier.

    Args:
        file_path (Path): Chemin vers le fichier à hasher.

    Returns:
        str: Hash SHA256 du fichier sous forme hexadécimale.
    """
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(64*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest() -> dict:
    """Génère le manifest du client avec hash SHA256 de tous les fichiers.

    Le manifest contient :
        - version : version actuelle du client
        - base_url : URL de base pour télécharger les fichiers
        - files : dictionnaire {chemin relatif: hash SHA256}

    Retourne également le sauvegarde dans CACHE_FILE pour debug ou vérification.

    Returns:
        dict: Manifest complet du client.
    """
    files = {}
    for file_path in CLIENT_DIR.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(CLIENT_DIR).as_posix()
            files[rel_path] = sha256_file(file_path)

    manifest = {
        "version": VERSION,
        "base_url": BASE_URL,
        "files": files
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

    return manifest


def manifest_needs_update() -> bool:
    """Détermine si le manifest doit être régénéré en fonction de la modification
    des fichiers dans CLIENT_DIR.

    Vérifie la date de dernière modification (mtime) de tous les fichiers.
    Si un fichier a été modifié après la dernière génération, retourne True.

    Returns:
        bool: True si le manifest doit être mis à jour, False sinon.
    """
    global LAST_MOD
    latest_mtime = max((f.stat().st_mtime for f in CLIENT_DIR.rglob("*") if f.is_file()), default=0)
    if latest_mtime > LAST_MOD:
        LAST_MOD = latest_mtime
        return True
    return False


def update_manifest_cache():
    """Met à jour le manifest_cache si nécessaire.

    - Utilise un verrou (CACHE_LOCK) pour sécuriser l'accès concurrent.
    - Génère le manifest uniquement si le cache est vide ou si des fichiers ont changé.
    """
    global manifest_cache
    with CACHE_LOCK:
        if not manifest_cache or manifest_needs_update():
            manifest_cache = generate_manifest()


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
    update_manifest_cache()
    return manifest_cache
