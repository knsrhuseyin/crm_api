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


def create_zip_if_needed():
    """Crée le ZIP du client uniquement si nécessaire.

    - Ne fait rien si le ZIP existe et que les fichiers n'ont pas changé.
    - Utilise la date de modification des fichiers pour décider si une recréation est nécessaire.
    """
    global LAST_MOD
    # Vérifier que le dossier client existe
    if not CLIENT_DIR.exists() or not any(CLIENT_DIR.iterdir()):
        return FileNotFoundError(f"Dossier client {CLIENT_DIR} vide ou introuvable")

    # Vérifie la dernière modification
    latest_mtime = max((f.stat().st_mtime for f in CLIENT_DIR.rglob("*") if f.is_file()), default=0)

    # Si le ZIP existe et qu'aucun fichier n'a été modifié depuis la dernière création, on ne touche à rien
    if ZIP_PATH.exists() and latest_mtime <= LAST_MOD:
        return

    # Création du ZIP
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in sorted(Path(f"{CLIENT_DIR}/").rglob("*")):
            if file_path.is_file():
                archive_name = file_path.relative_to(CLIENT_DIR).as_posix()
                zip_file.write(file_path, arcname=archive_name)

    # Met à jour LAST_MOD pour ne pas recréer inutilement
    LAST_MOD = latest_mtime


def update_manifest_cache():
    """Met à jour le manifest_cache si nécessaire.

    - Utilise un verrou (CACHE_LOCK) pour sécuriser l'accès concurrent.
    - Génère le manifest uniquement si le cache est vide ou si des fichiers ont changé.
    """
    global manifest_cache
    create_zip_if_needed()
    with CACHE_LOCK:
        if not manifest_cache or manifest_needs_update():
            manifest_cache = generate_manifest()
            return manifest_cache
        return manifest_cache
