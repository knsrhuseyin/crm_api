import logging
from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from API_DATABASE.auth import db_dependency, create_access_token, TOKEN_EXPIRES, verify_pwd, get_current_user
from API_DATABASE.models import User, Token


auth_router = APIRouter(prefix="/auth", tags=['auth'])

# Auth Endpoints
@auth_router.post('/token', response_model=Token)
def login_for_access_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=404, detail="Wrong info !")

    if not user.is_active:
        raise HTTPException(status_code=404, detail="Inactive User")

    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(data={"sub":user.email}, expires_delta=access_token_expires)
    response = {"access_token": access_token, "token_type": "bearer"}
    print(response)
    return response


@auth_router.get("/verify_token")
def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }

