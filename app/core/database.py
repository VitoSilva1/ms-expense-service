import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Vicente5150.@localhost:3306/userdb",
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that scopes a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

