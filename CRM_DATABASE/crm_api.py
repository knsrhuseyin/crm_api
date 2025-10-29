
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
    db = SessionCRM()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

crm_router = APIRouter(prefix="/crm", tags=['CRM Database management'])

@crm_router.get("/")
def root(current_user: user_dependency, db: db_dependency):
    if current_user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed !')
    elif db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is inactive !")
    return {"current_user": current_user}


@crm_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: db_dependency, current_user: user_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@crm_router.get("/users/email/{user_email}", response_model=UserResponse)
def get_user_with_email(user_email: str, db: db_dependency, current_user: user_dependency):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@crm_router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: db_dependency, current_user: user_dependency):
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
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist !")

    db.delete(db_user)
    db.commit()
    return {"message": "User Deleted"}


# Get all Users
@crm_router.get("/users/", response_model=List[UserResponse])
def get_all_users(db: db_dependency, current_user: user_dependency):
    return db.query(User).all()
