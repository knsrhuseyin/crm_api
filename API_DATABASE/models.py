# Pydantic Models (Dataclass)
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# DataBase Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class ConfigDict:
        from_attributes = True


# New Pydantic Models
class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
