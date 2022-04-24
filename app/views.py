import os
from datetime import datetime

from dotenv import load_dotenv
from psycopg2._range import DateTimeRange
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import PhoneNumber

from app.models import Housing, HousingCategory, CharacteristicType, Characteristic, User, Request

load_dotenv()

DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

engine = create_engine(
    f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
)

Session = sessionmaker(engine)


with Session() as session:
    client = session.query(User).filter(User.id == 2).all()[0]
    owner = session.query(User).filter(User.id == 1).all()[0]
    housing = session.query(Housing).all()[0]

    print(dir(housing.requests[0].during))
    # print(obj)
    session.commit()
