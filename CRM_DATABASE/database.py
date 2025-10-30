from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import utils

DATABASE_URL = utils.DATABASE_URL

crm_DB_engine = create_engine(DATABASE_URL)
SessionCRM = sessionmaker(autocommit=False, autoflush=False, bind=crm_DB_engine)
