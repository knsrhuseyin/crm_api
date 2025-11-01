"""
models.py
=========

Module permettant de créer les models des utilisateurs du CRM.

Dependencies:
    sqlalchemy: Module permettant de faire des requêtes SQL.
    pydantic: Module permettant de faire des models SQL.
"""

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# DataBase Model
class User(Base):
    """Model d'un utilisateur du CRM.

    Hérite de Base.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    telephone = Column(String(10), nullable=True)


# Pydantic Models (Dataclass)
class UserCreate(BaseModel):
    """Model des données nécessaires pour créer un utilisateur.

    Hérite de Base.
    """
    name: str
    first_name: str
    email: str
    telephone: str


class UserResponse(BaseModel):
    """Model d'une réponse d'un utilisateur du CRM.

    Hérite de BaseModel.
    """
    id: int
    name: str
    first_name: str
    email: str
    telephone: str

    class ConfigDict:
        """
        Class interne permet de configurer la forme des données.
        """
        from_attributes = True
