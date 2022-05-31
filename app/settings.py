import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_HOST = os.environ.get("DATABASE_HOST", "db")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "postgres")
DATABASE_USER = os.environ.get("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "postgres")

engine = create_engine(
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

Session = sessionmaker(engine)


def get_db() -> sessionmaker:
    db = Session()
    try:
        yield db
    finally:
        db.close()


MEDIA_URL = "/hosting/media/"
