# Database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

auth_db_engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})
SessionAuthDB = sessionmaker(autocommit=False, autoflush=False, bind=auth_db_engine)
