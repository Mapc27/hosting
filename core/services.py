import os
import uuid
from typing import Union

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.settings import MEDIA_URL
from core.models import Chat, User, Housing, HousingImage


def get_chat_short_(user_id: int, chat_id: int, db: Session) -> dict:
    sql_statement = f"""
        select json_build_object(
        'chat_id', chat.id,
        'companion', json_build_object('id', "user".id, 'name', "user".name, 'surname', "user".surname, '_phone_number',
                 "user"._phone_number, 'phone_country_code', "user".phone_country_code, 'email', "user".email, 'image',
                  "user".image),
        'last_message', chat_message,
        'unread_message_count', (select count(id) from chat_message where chat_message.chat_id = chat.id
         and chat_message.user_id != {user_id} and chat_message.read = false)
            )
        from chat left join chat_message on chat.id = chat_message.chat_id, "user"
        where chat.id = {chat_id} and {user_id} in (chat.user1_id, chat.user2_id) and
         "user".id in (chat.user1_id, chat.user2_id) and {user_id} != "user".id
        and (chat_message.created_at is null or chat_message.created_at =
        (select max (chat_message.created_at) from chat_message where chat_id = chat.id));
    """
    result = db.execute(sql_statement)
    result_dict = {}
    for i in result:
        result_dict = i[0]
        break
    return result_dict


def create_chat_(user1: User, user2: User, db: Session) -> Union[Chat, None]:
    if (
        db.query(Chat)
        .filter(Chat.user1_id == user1.id, Chat.user2_id == user2.id)
        .first()
    ):
        return None

    chat: Chat = Chat(user1_id=user1.id, user2_id=user2.id)
    db.add(chat)
    db.commit()
    return chat


def get_housing(user: User, housing_id: int, db: Session) -> Union[None, Housing]:
    if not user:
        return None
    housing: Housing = (
        db.query(Housing)
        .filter(Housing.user_id == user.id, Housing.id == housing_id)
        .first()
    )
    return housing


async def save_image(file_path: str, image: UploadFile) -> None:
    contents = await image.read()
    with open(file_path, "wb") as file:
        file.write(contents)


def replace_main_housing_image(
    housing_image: HousingImage, housing_id: int, db: Session
) -> Union[HousingImage, None]:
    main_image = (
        db.query(HousingImage)
        .filter(HousingImage.is_main == True, HousingImage.housing_id == housing_id)
        .first()
    )
    if not main_image:
        return None
    main_image.is_main = None
    db.commit()
    housing_image.is_main = True
    db.add(housing_image)
    db.commit()
    return housing_image


async def create_housing_image_(
    image: UploadFile, housing_id: int, db: Session, is_main: Union[None, bool]
) -> HousingImage:
    if (
        db.query(HousingImage).filter(HousingImage.housing_id == housing_id).count()
        == 0
    ):
        is_main = True

    file_name = f'{uuid.uuid4()}.{image.filename.split(".")[-1]}'
    housing_image: HousingImage = HousingImage(
        housing_id=housing_id, is_main=is_main, file_name=file_name
    )
    db.add(housing_image)

    try:
        db.commit()
    # image with is_main = True already exists, so move is_main parameter ...
    except IntegrityError:
        db.rollback()
        replace_main_housing_image(housing_image, housing_id, db)

    file_path = f"../{MEDIA_URL}housings/{housing_image.file_name}"
    await save_image(file_path, image)

    return housing_image


def delete_housing_image_(
    housing_id: int, image_id: int, db: Session
) -> Union[HousingImage, None]:
    housing_image: HousingImage = (
        db.query(HousingImage)
        .filter(HousingImage.id == image_id, HousingImage.housing_id == housing_id)
        .first()
    )
    if not housing_image:
        return None
    file_path = f"../{MEDIA_URL}housings/{housing_image.file_name}"
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(FileNotFoundError)

    db.delete(housing_image)
    db.commit()
    if housing_image.is_main:
        db.query(HousingImage).filter(
            HousingImage.housing_id == housing_image.housing_id
        ).first().is_main = True
    db.commit()
    return housing_image


def set_main_housing_image_(
    housing_id: int, image_id: int, db: Session
) -> Union[None, HousingImage]:
    housing_image: HousingImage = (
        db.query(HousingImage)
        .filter(HousingImage.id == image_id, HousingImage.housing_id == housing_id)
        .first()
    )

    if not housing_image:
        return None

    return replace_main_housing_image(housing_image, housing_id, db)
