from core.models import (
    Housing,
    ComfortCategory,
    Comfort,
    HousingComfort,
    User,
)
from app.settings import Session


def test() -> None:
    with Session() as session:
        user = User(email="123@gmail.com", password="1231")
        print(user.phone_number)
        # session.add(user)
        session.commit()


if __name__ == "__main__":
    test()
