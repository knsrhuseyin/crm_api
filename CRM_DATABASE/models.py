from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# DataBase Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    telephone = Column(String(10), nullable=True)


# Pydantic Models (Dataclass)
class UserCreate(BaseModel):
    name: str
    first_name: str
    email: str
    telephone: str


class UserResponse(BaseModel):
    id: int
    name: str
    first_name: str
    email: str
    telephone: str

    class ConfigDict:
        from_attributes = True
