"""
crm_api.py
==========

Module contenant les requêtes et les fonctions à éxectuer pour les utilisateurs du CRM.

Dependencies:
    fastapi: Module principal du programme permettant de créer une API avec une documentation automatique.
    sqlalchemy: Module permettant de faire des requêtes SQL.
    starlette: Module permettant d'avoir des status code HTTP.
"""

from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from API_DATABASE.auth import user_dependency
from CRM_DATABASE.database import crm_DB_engine, SessionCRM
from CRM_DATABASE.models import UserResponse, UserCreate, User, Base

Base.metadata.create_all(bind=crm_DB_engine)


def get_db():
    """
    Fonction permettant de vérifier la base de donnée du CRM.
    """
    db = SessionCRM()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

crm_router = APIRouter(prefix="/crm", tags=['CRM Database management'])


@crm_router.get("/")
def root(current_user: user_dependency, db: db_dependency):
    """Fonction racine de la requête

    Args:
        current_user (user_dependency): Vérifie l'utilisateur courant.
        db (db_dependency): Vérifie la base de donnée

    Returns:
        dict: L'utilisateur courant si connecté.

    Raises:
        HTTPException: Si l'utilisateur n'est pas connecté ou que l'accès à la base de donnée est impossible.
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed !')
    elif db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is inactive !")
    return {"current_user": current_user}


@crm_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: db_dependency, current_user: user_dependency):
    """Fonction permettant de renvoyant un utilisateur du CRM via son ID.

    Args:
        user_id (int): L'ID de l'utilisateur à renvoyer.
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie l'utilisateur.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@crm_router.get("/users/email/{user_email}", response_model=UserResponse)
def get_user_with_email(user_email: str, db: db_dependency, current_user: user_dependency):
    """Fonction permettant de renvoyant un utilisateur du CRM via son email.

    Args:
        user_email (str): L'email de l'utilisateur à renvoyer.
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie l'utilisateur.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas.
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@crm_router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: db_dependency, current_user: user_dependency):
    """Fonction permettant de créer un utilisateur.

    Args:
        user (UserCreate): Les informations de l'utilisateur à créer.
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie le nouvel utilisateur.

    Raises:
        HTTPException: Si l'utilisateur existe déjà.
    """
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="User already exists!")

    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Update user
@crm_router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: db_dependency, current_user: user_dependency):
    """Fonction permettant de mettre à jour un utilisateur du CRM via son ID.

    Args:
        user_id (int): L'ID de l'utilisateur à modifier.
        user (UserCreate): Les nouvelles informations de l'utilisateur.
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie l'utilisateur.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas ou qu'il existe déjà.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist!")

    for field, value in user.dict().items():
        setattr(db_user, field, value)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=404, detail="User already exists!")

    db.refresh(db_user)
    return db_user


# Delete User
@crm_router.delete("/users/{user_id}")
def delete_user(user_id: int, db: db_dependency, current_user: user_dependency):
    """Fonction permettant de supprimer un utilisateur du CRM via son ID.

    Args:
        user_id (int): L'ID de l'utilisateur à supprimer.
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie un dictionnaire pour confirmer que l'utilisateur est supprimé

    Raises:
        HTTPException: Si l'utilisateur n'existe pas.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist !")

    db.delete(db_user)
    db.commit()
    return {"message": "User Deleted"}


# Get all Users
@crm_router.get("/users/", response_model=List[UserResponse])
def get_all_users(db: db_dependency, current_user: user_dependency):
    """Fonction permettant de renvoyer tout les utilisateurs du CRM.

    Args:
        db (db_dependency): Vérifie la base de donnée.
        current_user (user_dependency): Vérifie l'utilisateur courant.

    Returns:
        dict: Renvoie les utilisateurs.
    """
    return db.query(User).all()
