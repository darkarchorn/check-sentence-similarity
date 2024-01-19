from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()


SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a Base class
Base = declarative_base()


def getDatabase():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
