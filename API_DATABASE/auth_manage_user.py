from typing import List

from fastapi import APIRouter, HTTPException, Depends

from API_DATABASE.auth import user_dependency, db_dependency, get_pwd_hash
from API_DATABASE.models import User, UserResponse, UserCreate


def get_current_active_user(current_user: user_dependency):
    if not current_user.is_active:
        raise HTTPException(status_code=404, detail="Inactive User")
    return current_user

auth_manage_user_router = APIRouter(prefix="/auth/user", tags=['Authentication API User Manager'])

@auth_manage_user_router.get("/")
def root(current_user: user_dependency):
    if current_user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed !')
    return {"Current User": current_user}

@auth_manage_user_router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@auth_manage_user_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: user_dependency, db: db_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@auth_manage_user_router.post("/create/", response_model=UserResponse)
def create_user(user: UserCreate, db: db_dependency):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="User already exists!")

    hashed_password = get_pwd_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_pwd=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Update user
@auth_manage_user_router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update_user: UserCreate, current_user: user_dependency, db: db_dependency):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist!")

    db_user.name = update_user.name
    db_user.email = update_user.email
    db_user.role = update_user.role

    db.commit()
    db.refresh(db_user)
    return db_user


# Delete User
@auth_manage_user_router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: user_dependency, db: db_dependency):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist !")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=404, detail="You cannot delete yourself!")

    db.delete(db_user)
    db.commit()
    return {"message": "User Deleted"}


# Get all Users
@auth_manage_user_router.get("/users/", response_model=List[UserResponse])
def get_all_users(db: db_dependency, current_user: user_dependency):
    return db.query(User).all()
