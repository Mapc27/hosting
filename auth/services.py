import os
import uuid
from typing import Union

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.settings import MEDIA_FOLDER
from core.models import LikedHousing, User, Housing, HousingImage
from core.services import save_image


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


async def create_user_image_(image: UploadFile, user: User, db: Session) -> User:
    if user.image:
        delete_user_image_(user, db)
    file_name = f'{uuid.uuid4()}.{image.filename.split(".")[-1]}'
    user.image = file_name
    db.add(user)
    db.commit()

    file_path = f"{MEDIA_FOLDER}/users/{file_name}"

    await save_image(file_path, image)

    return user


def delete_user_image_(user: User, db: Session) -> None:
    if not user.image:
        return None

    file_path = f"{MEDIA_FOLDER}/users/{user.image}"
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(FileNotFoundError)
    user.image = None
    db.add(user)
    db.commit()
