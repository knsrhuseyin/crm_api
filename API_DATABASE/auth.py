"""
auth.py
=======

Dependencies:
    fastapi: Module principal pour créer des API avec documentation automatique.
    jwt: Pour créer des jetons d'accès JWT.
    passlib: Pour crypter les mots de passe.
    sqlalchemy: Pour gérer la base de données via ORM.
"""

from datetime import datetime, timedelta
from typing import Optional, Annotated

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing_extensions import Any

from env_var import SECRET_KEY, ALGORITHM, TOKEN_EXPIRES
from API_DATABASE.database import auth_db_engine, SessionAuthDB
from API_DATABASE.models import User, Base, TokenData

# Configuration de cryptage et OAuth2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=auth_db_engine)


def get_db() -> Session:
    """Fournit une session de base de données pour les opérations CRUD.

    Yields:
        Session: Une session SQLAlchemy pour interagir avec la base de données.
    """
    db = SessionAuthDB()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Security Functions
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    """Vérifie si un mot de passe en clair correspond à un mot de passe hashé.

    Args:
        plain_pwd (str): Le mot de passe en clair.
        hashed_pwd (str): Le mot de passe hashé.

    Returns:
        bool: True si le mot de passe correspond, False sinon.
    """
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_pwd_hash(password: str) -> str:
    """Crée un hash sécurisé pour un mot de passe.

    Args:
        password (str): Le mot de passe en clair.

    Returns:
        str: Le mot de passe hashé.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Génère un jeton JWT pour un utilisateur.

    Args:
        data (dict): Les données à encoder dans le jeton (ex: {"sub": email}).
        expires_delta (Optional[timedelta]): Durée avant expiration du jeton. Défaut à 15 minutes.

    Returns:
        str: Le jeton JWT encodé.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Vérifie un jeton JWT et retourne ses données.

    Args:
        token (str): Le jeton JWT.

    Returns:
        TokenData: Objet contenant l'email de l'utilisateur.

    Raises:
        HTTPException: Si le jeton est invalide ou l'utilisateur inconnu.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(email=email)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Auth Dependencies
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency
) -> Any:
    """Récupère l'utilisateur courant à partir du jeton JWT.

    Args:
        token (str): Jeton d'accès de l'utilisateur.
        db (Session): Session de la base de données.

    Returns:
        Any: Objet User de l'utilisateur courant.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas ou jeton invalide.
    """
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


user_dependency = Annotated[dict, Depends(get_current_user)]
