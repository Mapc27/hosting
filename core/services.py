from sqlalchemy.orm import Session

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
)
from core.schemas import (
    HouseCreate,
    CategoryCreate,
    HousingTypeCreate,
    ComfortCategoryCreate,
    ComfortCreate,
    HousingPricingCreate,
)


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
