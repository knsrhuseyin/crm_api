"""
database.py
===========

Module permettant de récupérer la base de donnée du CRM.

Dependencies:
    sqlalchemy: Module permettant de faire des requêtes SQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import env_var

DATABASE_URL = env_var.DATABASE_URL

crm_DB_engine = create_engine(DATABASE_URL)
SessionCRM = sessionmaker(autocommit=False, autoflush=False, bind=crm_DB_engine)
