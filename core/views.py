from core.models import (
    Housing,
    ComfortCategory,
    Comfort,
    HousingComfort,
)
from app.settings import Session


def test() -> None:
    with Session() as session:
        housing = session.query(Housing).all()[0]
        cc = session.query(ComfortCategory).all()[0]
        c = session.query(Comfort).all()[0]
        hc = session.query(HousingComfort).all()[0]
        print(housing)
        print(cc)
        print(c)
        print(hc)

        session.commit()
