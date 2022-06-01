import os
import uuid
from typing import Union, Any

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.settings import MEDIA_FOLDER
from core.models import (
    Chat,
    User,
    HousingCategory,
    HousingType,
    Housing,
    ComfortCategory,
    Comfort,
    HousingComfort,
    HousingPricing,
    HousingImage,
    Characteristic,
    Rule,
    HousingRule,
    CharacteristicType,
)
from core.schemas import (
    HouseCreate,
    CategoryCreate,
    HousingTypeCreate,
    ComfortCategoryCreate,
    ComfortCreate,
    HousingPricingCreate,
)


def get_pagination_data(db: Session, page: int = 0, limit: int = 10) -> Any:
    data = db.query(Housing).offset(page).limit(limit).all()
    return data


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


def get_housing_by_user(
    user: User, housing_id: int, db: Session
) -> Union[None, Housing]:
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

    file_path = f"{MEDIA_FOLDER}/housings/{housing_image.file_name}"

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
    file_path = f"{MEDIA_FOLDER}/housings/{housing_image.file_name}"
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


def create_category(category_scheme: CategoryCreate, db: Session) -> HousingCategory:
    category: HousingCategory = HousingCategory(
        name=category_scheme.name,
        description=category_scheme.description,
        level=category_scheme.level,
    )
    db.add(category)
    db.commit()
    return category


def create_housing_type(type_scheme: HousingTypeCreate, db: Session) -> HousingType:
    housing_type: HousingType = HousingType(
        name=type_scheme.name, description=type_scheme.description
    )
    db.add(housing_type)
    db.commit()
    return housing_type


def create_housing(
    house_scheme: HouseCreate,
    user: User,
    category: HousingCategory,
    housing_type: HousingType,
    db: Session,
) -> Housing:
    housing: Housing = Housing(
        name=house_scheme.name,
        address=house_scheme.address,
        user_id=user.id,
        description=house_scheme.description,
        category_id=category.id,
        type_id=housing_type.id,
    )
    db.add(housing)
    db.commit()
    return housing


def create_comfort_category(
    comfort_category_scheme: ComfortCategoryCreate, db: Session
) -> ComfortCategory:
    category: ComfortCategory = ComfortCategory(name=comfort_category_scheme.name)
    db.add(category)
    db.commit()
    return category


def create_comfort(
    comfort_scheme: ComfortCreate, category: ComfortCategory, db: Session
) -> Comfort:
    comfort: Comfort = Comfort(name=comfort_scheme.name, category_id=category.id)
    db.add(comfort)
    db.commit()
    return comfort


def create_housing_comfort(
    comfort: Comfort, housing: Housing, db: Session
) -> HousingComfort:
    housing_comfort: HousingComfort = HousingComfort(
        housing_id=housing.id, comfort_id=comfort.id
    )
    db.add(housing_comfort)
    db.commit()
    return housing_comfort


def create_housing_pricing(
    housing_pricing_scheme: HousingPricingCreate, housing: Housing, db: Session
) -> HousingPricing:
    housing_pricing: HousingPricing = HousingPricing(
        per_night=housing_pricing_scheme.per_night,
        cleaning=housing_pricing_scheme.cleaning,
        service=housing_pricing_scheme.service,
        discount_per_week=housing_pricing_scheme.discount_per_week,
        discount_per_month=housing_pricing_scheme.discount_per_month,
        housing_id=housing.id,
    )
    db.add(housing_pricing)
    db.commit()
    return housing_pricing


def get_housing_(housing_id: int, db: Session) -> dict:
    housing: Housing = db.query(Housing).filter(Housing.id == housing_id).first()
    if not housing:
        return {"detail": "Housing doesn't exists"}
    characteristics = (
        db.query(Characteristic).filter(Characteristic.housing_id == housing_id).all()
    )
    characteristics = [
        i.as_dict(extra_fields=["characteristic_type"]) for i in characteristics
    ]

    rules = (
        db.query(HousingRule, Rule)
        .filter(HousingRule.housing_id == housing_id, HousingRule.id == Rule.id)
        .all()
    )
    rules = [i.Rule.as_dict(extend=["updated_at", "created_at"]) for i in rules]

    comforts = (
        db.query(HousingComfort, Comfort, ComfortCategory)
        .filter(
            HousingComfort.housing_id == housing_id,
            Comfort.category_id == ComfortCategory.id,
            HousingComfort.comfort_id == Comfort.id,
        )
        .all()
    )

    comforts = [
        i.Comfort.as_dict(extend=["updated_at", "created_at"]) for i in comforts
    ]

    housing_dict = housing.as_dict(
        extra_fields=["user", "housing_images", "type", "calendar", "pricing"]
    )
    housing_dict["characteristics"] = characteristics
    housing_dict["rules"] = rules
    housing_dict["comforts"] = comforts
    return housing_dict


def create_housings_attrs_(db: Session) -> None:
    for model in (HousingType, HousingCategory, CharacteristicType):
        db.query(model).delete()
    db.commit()

    for name, description in {
        "Entire place": "A place all to yourself",
        "Shared room": "A sleeping space and common areas that may be shared with others",
        "Private room": "Your own room in a home or a hotel, plus some shared common spaces",
    }.items():
        housing_type = HousingType(name=name, description=description)
        db.add(housing_type)

    for name in (
        "Apartment",
        "House",
        "Secondary unit",
        "Unique space",
        "Bed and breakfast",
        "Boutique hotel",
    ):
        housing_category = HousingCategory(name=name)
        db.add(housing_category)

    for name in ("guests", "bedrooms", "beds", "baths"):
        characteristic_type = CharacteristicType(name=name)
        db.add(characteristic_type)
    db.commit()


def get_housing_fields_(db: Session) -> dict:
    return {
        "housing_types": [obj.as_dict() for obj in db.query(HousingType).all()],
        "characteristic_types": [
            obj.as_dict() for obj in db.query(CharacteristicType).all()
        ],
        "housing_categories": [
            obj.as_dict() for obj in db.query(HousingCategory).all()
        ],
    }
