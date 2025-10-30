from datetime import datetime, timedelta
from typing import Optional, Annotated

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import utils
from API_DATABASE.database import auth_db_engine, SessionAuthDB
from API_DATABASE.models import User, Base, TokenData

# Security Config
SECRET_KEY = utils.SECRET_KEY
ALGORITHM = utils.ALGORITHM
TOKEN_EXPIRES = int(utils.TOKEN_EXPIRES)

print(SECRET_KEY, ALGORITHM, TOKEN_EXPIRES)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

Base.metadata.create_all(bind=auth_db_engine)


def get_db():
    db = SessionAuthDB()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Security Functions
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    print(pwd_context.verify(plain_pwd, hashed_pwd))
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
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
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist",
                            headers={"WW-Authenticate": "Bearer"})
    return user


user_dependency = Annotated[dict, Depends(get_current_user)]
