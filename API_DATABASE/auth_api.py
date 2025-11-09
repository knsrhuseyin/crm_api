"""
auth_api.py
===========

Module gérant le côté API pour les requêtes d'authentification.

Dependencies:
    fastapi: Module principal pour créer une API avec documentation automatique.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from API_DATABASE.auth import (
    db_dependency,
    create_access_token,
    TOKEN_EXPIRES,
    verify_pwd,
    get_current_user,
)
from API_DATABASE.models import User, Token

auth_router = APIRouter(prefix="/auth", tags=["Auth API"])


# Auth Endpoints
@auth_router.post("/token", response_model=Token)
def login_for_access_token(
    db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """Génère un jeton d'accès pour un utilisateur qui se connecte via l'API.

    Args:
        db (Session): Session de la base de données pour interroger les utilisateurs.
        form_data (OAuth2PasswordRequestForm): Informations d'identification envoyées par l'utilisateur.

    Returns:
        dict: Contient le jeton d'accès et son type.

    Raises:
        HTTPException: Si les informations sont incorrectes ou si l'utilisateur est inactif.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=404, detail="Wrong info!")

    if not user.is_active:
        raise HTTPException(status_code=404, detail="Inactive User")

    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/verify_token")
def verify_token_endpoint(current_user: User = Depends(get_current_user)) -> dict:
    """Vérifie la validité du jeton et renvoie les informations de l'utilisateur.

    Args:
        current_user (User): L'utilisateur courant authentifié via le jeton.

    Returns:
        dict: Informations de l'utilisateur et statut de validation.
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        },
    }
