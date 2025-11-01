"""
auth_api.py
===========

Module gérant le côté API pour faire des requêtes et pouvoir se connecter à l'API.

Dependencies:
    fastapi: Module principal du programme permettant de créer une API avec une documentation automatique.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from API_DATABASE.auth import db_dependency, create_access_token, TOKEN_EXPIRES, verify_pwd, get_current_user
from API_DATABASE.models import User, Token

auth_router = APIRouter(prefix="/auth", tags=['auth'])


# Auth Endpoints
@auth_router.post('/token', response_model=Token)
def login_for_access_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    """Fonction permettant d'envoyant le jeton à l'utilisateur qui fait la requête.

    Args:
        db (db_dependency): Database de des utilisateurs ayant accès à l'API.
        form_data: Les informations de l'utilisateur ayant fait la requête.

    Returns:
        dict: Le jeton d'accès et son type.

    Raises:
         HTTPException: Si les données reçues ne sont pas corrects ou que l'utilisateur n'est pas considéré comme actif.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=404, detail="Wrong info !")

    if not user.is_active:
        raise HTTPException(status_code=404, detail="Inactive User")

    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    response = {"access_token": access_token, "token_type": "bearer"}
    return response


@auth_router.get("/verify_token")
def verify_token_endpoint(current_user: User = Depends(get_current_user)) -> dict:
    """Fonction permettant de vérifier le jeton d'accès après la requête d'un utilisateur de l'API.

    Args:
        current_user (User): L'utilisateur courant ayant fait la requête.

    Returns:
        dict: Les informations de l'utilisateur.
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }
