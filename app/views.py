import os
from datetime import datetime, date

from dotenv import load_dotenv
from psycopg2._range import DateTimeRange
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import PhoneNumber

from app.models import (
    Housing,
    HousingCategory,
    CharacteristicType,
    Characteristic,
    User,
    Request,
    HousingHistory,
    HousingReview,
)

load_dotenv()

DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

engine = create_engine(
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

Session = sessionmaker(engine)

Base = declarative_base()


def get_db() -> sessionmaker:
    db = Session()
    try:
        yield db
    finally:
        db.close()


# with Session() as session:
# #     # создать юзера
# # user = User(name='user1', surname='surname', phone_number=PhoneNumber('0123456789', 'RU'), email='email@mail.ru',
# #             birth_date=date(year=2022, month=4, day=20), password='123')
# # session.commit()
#
#     # получить юзера
#     user = session.query(User).all()[0]
#     print(type(user))
