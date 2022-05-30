from sqlalchemy.orm import Session

from core.models import Chat, User, HousingCategory, HousingType, Housing
from core.schemas import HouseCreate, CategoryCreate, HousingTypeCreate


def create_chat_(user1: User, user2: User, db: Session) -> int:
    chat: Chat = Chat(user1_id=user1.id, user2_id=user2.id)
    db.add(chat)
    db.commit()
    return chat.id


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
