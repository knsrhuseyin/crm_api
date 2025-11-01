"""
models.py
=========

Module créant les tables de la base de donnée contenant les utilisateurs de l'API.

Dependencies:
    sqlalchemy: Module permettant de faire des requêtes SQL.
    pydantic: Module permettant de faire des models SQL.
"""
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# DataBase Model
class User(Base):
    """Model d'un utilisateur de l'API.

    Hérite de Base.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class UserCreate(BaseModel):
    """Model des données nécessaires pour créer un utilisateur.

    Hérite de BaseModel.
    """
    name: str
    email: str
    role: str
    password: str


class UserResponse(BaseModel):
    """Model de la réponse de l'API lors d'une demande de vérification de l'utilisateur.

    Hérite de BaseModel.
    """
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class ConfigDict:
        """
        Class interne permet de configurer la forme des données.
        """
        from_attributes = True


# New Pydantic Models
class UserLogin(BaseModel):
    """Model des données nécessaires pour se connecter.

    Hérite de BaseModel.
    """
    email: str
    password: str


class Token(BaseModel):
    """Model de réponse d'un jeton d'accès.

    Hérite de BaseModel.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Model d'une donnée contenu dans le jeton.

    Hérite de BaseModel.
    """
    email: Optional[str] = None
