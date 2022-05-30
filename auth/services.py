from typing import Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import LikedHousing, User, Housing, HousingImage


def get_wishlist_(user: User, db: Session) -> Union[list, None]:
    query = (
        db.query(LikedHousing, Housing, HousingImage)
        .filter(
            LikedHousing.user_id == user.id,
            LikedHousing.housing_id == Housing.id,
            HousingImage.housing_id == Housing.id,
            HousingImage.is_main == True,
        )
        .all()
    )

    if not query:
        return None

    result = []
    for row in query:
        housing = row.Housing.as_dict()
        housing["main_image"] = row.HousingImage.as_dict()
        like: dict = row.LikedHousing.as_dict()
        like["housing"] = housing
        result.append(like)
    return result


def get_wish_(
    user: User,
    db: Session,
    housing_id: Union[int, None] = None,
    liked_housing_id: Union[int, None] = None,
) -> Union[dict, None]:
    if housing_id:
        query = (
            db.query(LikedHousing, Housing, HousingImage)
            .filter(
                LikedHousing.user_id == user.id,
                Housing.id == housing_id,
                LikedHousing.housing_id == housing_id,
                HousingImage.housing_id == housing_id,
                HousingImage.is_main == True,
            )
            .first()
        )
    elif liked_housing_id:
        query = (
            db.query(LikedHousing, Housing, HousingImage)
            .filter(
                LikedHousing.user_id == user.id,
                LikedHousing.id == liked_housing_id,
                LikedHousing.housing_id == Housing.id,
                HousingImage.housing_id == Housing.id,
                HousingImage.is_main == True,
            )
            .first()
        )
    else:
        return None

    if not query:
        return None

    housing: dict = query.Housing.as_dict()
    housing["main_image"] = query.HousingImage.as_dict()
    like: dict = query.LikedHousing.as_dict()
    like["housing"] = housing
    return like


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
    user: User,
    db: Session,
    liked_housing_id: Union[int, None] = None,
    housing_id: Union[int, None] = None,
) -> Union[LikedHousing, None]:
    liked_housing: LikedHousing
    if liked_housing_id:
        liked_housing = (
            db.query(LikedHousing)
            .filter(
                LikedHousing.user_id == user.id, LikedHousing.id == liked_housing_id
            )
            .first()
        )
    elif housing_id:
        liked_housing = (
            db.query(LikedHousing)
            .filter(
                LikedHousing.user_id == user.id, LikedHousing.housing_id == housing_id
            )
            .first()
        )
    else:
        return None

    if not liked_housing:
        return None

    db.delete(liked_housing)
    db.commit()
    return liked_housing
