"""
utils.py
========

Module utilitaire qui récupère les variables d'environnement nécessaire au fonctionnement de l'API.

Dépendencies:
    dotenv: Module servant à récupérer les variables d'environnement local.
"""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRES = os.getenv("TOKEN_EXPIRES")
