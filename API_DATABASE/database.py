"""
database.py
===========

Module de configuration d'une base de données locale pour permettre l'accès
aux utilisateurs enregistrés.

Dependencies:
    sqlalchemy: Module pour interagir avec des bases de données SQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Création du moteur de base de données pour SQLite
auth_db_engine = create_engine(
    "sqlite:///users.db", connect_args={"check_same_thread": False}
)

# Création d'une fabrique de sessions pour interagir avec la base de données
SessionAuthDB = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=auth_db_engine
)
