"""
manifest_generator.py
=====================

Module pour générer et gérer le manifest du client CRM, incluant :
- Hash SHA256 des fichiers.
- Manifest mis en cache pour éviter les recalculs inutiles.

Dependencies:
    threading, zipfile, hashlib, json, pathlib, typing
"""

import threading
import zipfile
import hashlib
import json
from pathlib import Path
from typing import Dict

from env_var import CLIENT_DIR, CONFIG_FILE

# =======================
# Configuration
# =======================
CLIENT_DIR = Path(CLIENT_DIR)
CACHE_FILE = Path(f"{CLIENT_DIR.parent}/manifest_cache.json")
CONFIG_FILE = Path(CONFIG_FILE)
ZIP_PATH = Path(f"{CLIENT_DIR.parent}/CRMClient.zip")

# =======================
# Variables cache
# =======================
manifest_cache: Dict = {}
LAST_MOD = 0
CACHE_LOCK = threading.Lock()


def read_internal_config() -> dict:
    """Lit le fichier JSON interne contenant la version et l'URL de téléchargement.

    Returns:
        dict: Dictionnaire avec les clés 'version' et 'download_url'.

    Raises:
        FileNotFoundError: Si le fichier de configuration est introuvable.
        KeyError: Si les clés attendues ne sont pas présentes.
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Le fichier de configuration interne {CONFIG_FILE} est introuvable."
        )

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    if "version" not in config or "download_url" not in config:
        raise KeyError(
            f"Le fichier {CONFIG_FILE} doit contenir les clés 'version' et 'download_url'."
        )

    return config


def sha256_file(file_path: Path) -> str:
    """Calcule le hash SHA256 d'un fichier.

    Args:
        file_path (Path): Chemin vers le fichier à hasher.

    Returns:
        str: Hash SHA256 sous forme hexadécimale.
    """
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest() -> dict:
    """Génère le manifest du client avec le hash SHA256 de tous les fichiers.

    Le manifest inclut la version et l'URL de téléchargement depuis la config interne.

    Returns:
        dict: Manifest complet incluant 'version', 'download_url' et 'files' avec leurs hash SHA256.
    """
    config = read_internal_config()
    version = config["version"]
    download_url = config["download_url"]

    CLIENT_DIR.mkdir(parents=True, exist_ok=True)

    files = {}
    for file_path in sorted(CLIENT_DIR.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(CLIENT_DIR).as_posix()
            files[rel_path] = sha256_file(file_path)

    manifest = {
        "version": version,
        "download_url": download_url,
        "files": files,
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(manifest, f, indent=4, sort_keys=True)

    return manifest


def manifest_needs_update() -> bool:
    """Détermine si le manifest doit être régénéré.

    Vérifie la date de dernière modification de tous les fichiers du CLIENT_DIR.
    Si un fichier a été modifié depuis la dernière génération, retourne True.

    Returns:
        bool: True si le manifest doit être mis à jour, False sinon.
    """
    global LAST_MOD
    latest_mtime = max(
        (f.stat().st_mtime for f in CLIENT_DIR.rglob("*") if f.is_file()), default=0
    )
    if latest_mtime > LAST_MOD:
        LAST_MOD = latest_mtime
        return True
    return False


def update_manifest_cache() -> dict:
    """Met à jour le manifest_cache si nécessaire.

    - Utilise un verrou (CACHE_LOCK) pour sécuriser l'accès concurrent.
    - Génère le manifest uniquement si le cache est vide ou si des fichiers ont changé.
    - Crée le ZIP si besoin.

    Returns:
        dict: Le manifest mis à jour.
    """
    global manifest_cache
    with CACHE_LOCK:
        if not manifest_cache or manifest_needs_update():
            manifest_cache = generate_manifest()
        return manifest_cache
