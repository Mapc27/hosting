from typing import Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import LikedHousing, User


def get_wishlist_(user: User, db: Session) -> list:
    return [
        like.as_dict()
        for like in db.query(LikedHousing).filter(LikedHousing.user_id == user.id).all()
    ]


def create_wishlist_(
    user: User, housing_id: int, db: Session
) -> Union[LikedHousing, None]:
    liked_housing: LikedHousing = LikedHousing(user_id=user.id, housing_id=housing_id)
    db.add(liked_housing)
    try:
        db.commit()
    except IntegrityError:
        return None
    return liked_housing


def delete_wishlist_(
    user: User, housing_id: int, db: Session
) -> Union[LikedHousing, None]:
    liked_housing: LikedHousing = (
        db.query(LikedHousing)
        .filter(LikedHousing.user_id == user.id, LikedHousing.housing_id == housing_id)
        .first()
    )
    if not liked_housing:
        return None

    db.delete(liked_housing)
    db.commit()
    return liked_housing
