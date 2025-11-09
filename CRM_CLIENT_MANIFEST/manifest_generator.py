import threading
from pathlib import Path
import hashlib
import json
from typing import Dict

from env_var import CLIENT_DIR, CONFIG_DIR

# =======================
# Configuration
# =======================
CLIENT_DIR = Path(f"{CLIENT_DIR}/crm-client")
CACHE_FILE = Path(f"{CLIENT_DIR}/manifest_cache.json")
CONFIG_FILE = Path(CONFIG_DIR)

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
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Le fichier de configuration interne {CONFIG_FILE} est introuvable.")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    # Vérifie que les clés attendues sont présentes
    if "version" not in config or "download_url" not in config:
        raise KeyError(f"Le fichier {CONFIG_FILE} doit contenir les clés 'version' et 'download_url'.")

    return config


def sha256_file(file_path: Path) -> str:
    """Calcule le hash SHA256 d'un fichier.

    Args:
        file_path (Path): Chemin vers le fichier à hasher.

    Returns:
        str: Hash SHA256 du fichier sous forme hexadécimale.
    """
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest() -> dict:
    """Génère le manifest du client avec hash SHA256 de tous les fichiers."""

    # Lire la config interne
    config = read_internal_config()
    version = config["version"]
    download_url = config["download_url"]

    # S'assurer que le dossier CLIENT_DIR existe
    CLIENT_DIR.mkdir(parents=True, exist_ok=True)

    # Hash des fichiers
    files = {}
    for file_path in sorted(CLIENT_DIR.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(CLIENT_DIR).as_posix()
            files[rel_path] = sha256_file(file_path)

    manifest = {
        "version": version,
        "download_url": download_url,
        "files": files
    }

    # Sauvegarde stable
    with open(CACHE_FILE, "w") as f:
        json.dump(manifest, f, indent=4, sort_keys=True)

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
            return manifest_cache
        return manifest_cache
