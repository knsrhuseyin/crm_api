"""
models.py
=========

Module définissant les tables et modèles Pydantic pour la base de données
des utilisateurs de l'API.

Dependencies:
    sqlalchemy: Pour définir les modèles SQL et interagir avec la base de données.
    pydantic: Pour définir les modèles de données et valider les entrées.
"""

from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """Représente un utilisateur dans la base de données.

    Attributes:
        id (int): Identifiant unique de l'utilisateur.
        name (str): Nom de l'utilisateur.
        email (str): Adresse e-mail unique de l'utilisateur.
        role (str): Rôle de l'utilisateur.
        hashed_pwd (str): Mot de passe haché.
        is_active (bool): Indique si l'utilisateur est actif.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class UserCreate(BaseModel):
    """Données nécessaires pour créer un nouvel utilisateur.

    Attributes:
        name (str): Nom de l'utilisateur.
        email (str): Adresse e-mail.
        role (str): Rôle de l'utilisateur.
        password (str): Mot de passe en clair.
    """
    name: str
    email: str
    role: str
    password: str


class UserResponse(BaseModel):
    """Données renvoyées par l'API pour un utilisateur.

    Attributes:
        id (int): Identifiant unique de l'utilisateur.
        name (str): Nom de l'utilisateur.
        email (str): Adresse e-mail.
        role (str): Rôle de l'utilisateur.
        is_active (bool): Indique si l'utilisateur est actif.
    """
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class ConfigDict:
        """Configuration interne de Pydantic pour la conversion depuis SQLAlchemy."""
        from_attributes = True


class UserLogin(BaseModel):
    """Données nécessaires pour se connecter à l'API.

    Attributes:
        email (str): Adresse e-mail de l'utilisateur.
        password (str): Mot de passe en clair.
    """
    email: str
    password: str


class Token(BaseModel):
    """Jeton d'accès renvoyé par l'API après authentification.

    Attributes:
        access_token (str): Valeur du jeton.
        token_type (str): Type du jeton (ex: 'bearer').
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Données extraites du jeton d'accès.

    Attributes:
        email (Optional[str]): Adresse e-mail associée au jeton.
    """
    email: Optional[str] = None
