"""
env_var.py
==========

Module utilitaire pour récupérer les variables d'environnement nécessaires
au fonctionnement de l'API.

Dependencies:
    dotenv: Pour charger les variables d'environnement depuis un fichier .env.
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Variables de configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Variables pour la gestion des tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRES = int(os.getenv("TOKEN_EXPIRES"))

# Variables liées au client et à la configuration
CLIENT_DIR = os.getenv("CLIENT_DIR")
CONFIG_FILE = os.getenv("CONFIG_FILE")
