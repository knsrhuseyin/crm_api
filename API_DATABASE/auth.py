"""
auth.py
=======

Dependencies:
    fastapi: Module principal du programme permettant de créer des API avec une documentation automatique.
    jwt: pour créer des jetons d'accès JWT.
    passlib: Pour crypter un mot de passe.
    sqlalchemy: Pour faire des requêtes SQL plus facilement et sans mettre du SQL dans le code.
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

import env_var
from API_DATABASE.database import auth_db_engine, SessionAuthDB
from API_DATABASE.models import User, Base, TokenData

# Security Config
SECRET_KEY = utils.SECRET_KEY
ALGORITHM = utils.ALGORITHM
TOKEN_EXPIRES = int(env_var.TOKEN_EXPIRES)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

Base.metadata.create_all(bind=auth_db_engine)


def get_db():
    """
    Fonction pour vérifier si on peut se connecter à la base de donnée.
    """
    db = SessionAuthDB()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Security Functions
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    """Fonction pour vérifier si le mot de passe crypté correspond au mot de passe cité.

    Args:
        plain_pwd (str): le mot de passe.
        hashed_pwd (str): le mot de passe crypté.

    Returns:
        bool: True si le mot de passe correspond au mot de passe crypté, False sinon.
    """
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_pwd_hash(password: str) -> str:
    """Fonction pour crypter un mot de passe.

    Args:
        password (str): Le mot de passe à crypter.

    Returns:
        str: Le mot de passe crypté.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Fonction permettant de créer un jeton d'accès pour accéder à l'API.

    Args:
        data (dict): Les données de l'utilisateur.
        expires_delta: Optionnel, expiration du jeton.

    Returns:
        str: Le jeton d'accès.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Fonction permettant de vérifier si le jeton d'accès est valide.

    Args:
        token (str): Le jeton à vérifier.

    Returns:
        TokenData: Les données du jeton.

    Raises:
        HTTPException: Exception HTTP si le jeton n'est pas valide.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify credentials",
                                headers={"WW-Authenticate": "Bearer"})
        return TokenData(email=email)
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify credentials",
                            headers={"WW-Authenticate": "Bearer"})


# Auth Dependencies
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency) -> Any:
    """Fonction permettant de récupérer l'utilisateur courant en vérifiant le jeton.

    Args:
        token (str): Le jeton de l'utilisateur courant.
        db (db_dependency): Le database de l'utilisateur courant.

    Returns:
        Any: L'utilisateur courant.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas.
    """
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist",
                            headers={"WW-Authenticate": "Bearer"})
    return user


user_dependency = Annotated[dict, Depends(get_current_user)]
