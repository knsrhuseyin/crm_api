"""
database.py
===========

Module configurant une base de donnée locale permettant l'accès à la base de donnée pour les utilisateurs enregistrés.

Dependencies:
    sqlalchemy: Module permettant de faire des requêtes SQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

auth_db_engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})
SessionAuthDB = sessionmaker(autocommit=False, autoflush=False, bind=auth_db_engine)
