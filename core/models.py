from datetime import datetime, time, date
from decimal import Decimal
from typing import Optional, List, Union, Any

from psycopg2._range import DateTimeRange
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Boolean,
    CheckConstraint,
    Time,
    Float,
    Unicode,
    Date,
    Text,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.dialects.postgresql import TSRANGE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, composite, DeclarativeMeta, Mapped, registry
from sqlalchemy_utils import PhoneNumber
from sqlalchemy_utils.types.email import EmailType

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor


class BaseMixin(object):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())


class Housing(Base, BaseMixin):
    __tablename__ = "housing"
    __table_args__ = (
        ForeignKeyConstraint(
            ("category_id",),
            ("housing_category.id",),
            name="fk_on_housing_category",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("type_id",),
            ("housing_type.id",),
            name="fk_on_housing_type",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("user_id",),
            ("user.id",),
            name="fk_on_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    name: str = Column(String(50), nullable=False)
    description: str = Column(String(500), nullable=False)
    address: str = Column(String, nullable=False)
    status: Optional[bool] = Column(Boolean, default=False)
    images: Optional[str] = Column(String)

    category_id: Optional[int] = Column(Integer)
    type_id: Optional[int] = Column(Integer)
    user_id: Optional[int] = Column(Integer)

    calendar: "HousingCalendar" = relationship(
        "HousingCalendar", back_populates="housing", uselist=False
    )
    pricing: "HousingPricing" = relationship(
        "HousingPricing", back_populates="housing", uselist=False
    )
    category: "HousingCategory" = relationship(
        "HousingCategory", back_populates="housings", uselist=False
    )
    type: "HousingType" = relationship(
        "HousingType", back_populates="housings", uselist=False
    )
    user: "User" = relationship("User", back_populates="housings", uselist=False)

    housing_rules: List["HousingRule"] = relationship(
        "HousingRule", back_populates="housing", uselist=True, collection_class=list
    )
    characteristics: List["Characteristic"] = relationship(
        "Characteristic", back_populates="housing", uselist=True, collection_class=list
    )
    review_grades: List["ReviewGrade"] = relationship(
        "ReviewGrade", back_populates="housing", uselist=True, collection_class=list
    )
    requests: List["HousingRequest"] = relationship(
        "HousingRequest", back_populates="housing", uselist=True, collection_class=list
    )
    history: List["HousingHistory"] = relationship(
        "HousingHistory", back_populates="housing", uselist=True, collection_class=list
    )
    housing_comforts: List["HousingComfort"] = relationship(
        "HousingComfort", back_populates="housing", uselist=True, collection_class=list
    )
    housing_features: List["HousingFeature"] = relationship(
        "HousingFeature", back_populates="housing", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"description='{self.description}', "
            f"address='{self.address}')>"
        )


class CharacteristicType(Base, BaseMixin):
    __tablename__ = "characteristic_type"

    name: str = Column(String(50), nullable=False)

    characteristics: List["Characteristic"] = relationship(
        "Characteristic",
        back_populates="characteristic_type",
        uselist=True,
        collection_class=list,
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"characteristics='{self.characteristics}')>"
        )


class Characteristic(Base, BaseMixin):
    __tablename__ = "characteristic"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_amount"),
        UniqueConstraint(
            "housing_id",
            "characteristic_type_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("characteristic_type_id",),
            ("characteristic_type.id",),
            name="fk_on_characteristic_type",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    amount: int = Column(Integer, nullable=False, default=0)

    housing_id: int = Column(Integer, nullable=False)
    characteristic_type_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship(
        "Housing", back_populates="characteristics", uselist=False
    )
    characteristic_type: CharacteristicType = relationship(
        "CharacteristicType", back_populates="characteristics", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"housing='{self.housing}', "
            f"characteristic_type='{self.characteristic_type}', "
            f"amount='{self.amount}')>"
        )


class HousingCategory(Base, BaseMixin):
    __tablename__ = "housing_category"
    __table_args__ = (
        CheckConstraint("level >= 0 and level <= 2"),
        ForeignKeyConstraint(
            ("parent_id",),
            ("housing_category.id",),
            name="fk_on_yourself",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    name: str = Column(String(50), nullable=False)
    description: str = Column(String(100), nullable=False)
    level: int = Column(Integer, nullable=False)

    parent_id: int = Column(Integer, nullable=True)

    parent: "HousingCategory" = relationship("HousingCategory", uselist=False)
    housings: List[Housing] = relationship(
        "Housing", back_populates="category", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"description='{self.description}', "
            f"level='{self.level}', "
            f"parent='{self.parent}', "
            f"housings='{self.housings}')>"
        )


class HousingType(Base, BaseMixin):
    __tablename__ = "housing_type"

    name: str = Column(String(50), nullable=False)
    description: str = Column(String(100), nullable=False)

    housings: List[Housing] = relationship(
        "Housing", back_populates="type", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"description='{self.description}')>"
        )


class HousingCalendar(Base, BaseMixin):
    __tablename__ = "housing_calendar"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
        ),
        CheckConstraint(
            "min_nights >= 0 and max_nights >= 0",
            name="check_numbers_of_nights",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    during: DateTimeRange = Column(TSRANGE(), nullable=False)
    min_nights: int = Column(Integer, nullable=False)
    max_nights: int = Column(Integer, nullable=False)
    notification_diff_days: int = Column(Integer, nullable=False)
    notification_max_time: time = Column(Time, nullable=False)

    housing_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship("Housing", back_populates="calendar", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"during='{self.during}', "
            f"housing='{self.housing}')>"
        )


class HousingPricing(Base, BaseMixin):
    __tablename__ = "housing_pricing"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
        ),
        CheckConstraint(
            "per_night >= 0",
            name="check_per_night",
        ),
        CheckConstraint(
            "cleaning >= 0",
            name="check_cleaning",
        ),
        CheckConstraint(
            "service >= 0",
            name="check_service",
        ),
        CheckConstraint(
            "discount_per_week >= 0 and discount_per_week <= 100",
            name="check_discount_per_week",
        ),
        CheckConstraint(
            "discount_per_month >= 0 and discount_per_month <= 100",
            name="check_discount_per_month",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    per_night: int = Column(Integer, nullable=False)
    cleaning: int = Column(Integer, nullable=False)
    service: int = Column(Integer, nullable=False)
    discount_per_week: int = Column(Integer, nullable=False)
    discount_per_month: int = Column(Integer, nullable=False)

    housing_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship("Housing", back_populates="pricing", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"per_night='{self.per_night}', "
            f"housing='{self.housing}')>"
        )


class Rule(Base, BaseMixin):
    __tablename__ = "rule"

    name: str = Column(String, nullable=False)

    housing_rules: List["HousingRule"] = relationship(
        "HousingRule", back_populates="rule", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, " f"name='{self.name}')>"


class HousingRule(Base, BaseMixin):
    __tablename__ = "housing_rule"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
            "rule_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("rule_id",),
            ("rule.id",),
            name="fk_on_rule",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    housing_id: int = Column(Integer, nullable=False)
    rule_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship(
        "Housing", back_populates="housing_rules", uselist=False
    )
    rule: Rule = relationship("Rule", back_populates="housing_rules", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"rule='{self.rule}', "
            f"housing='{self.housing}')>"
        )


class ReviewCategory(Base, BaseMixin):
    __tablename__ = "review_category"

    name: str = Column(String, nullable=False)

    review_grades: List["ReviewGrade"] = relationship(
        "ReviewGrade",
        back_populates="review_category",
        uselist=True,
        collection_class=list,
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, " f"name='{self.name}')>"


class ReviewGrade(Base, BaseMixin):
    __tablename__ = "review_grade"
    __table_args__ = (
        CheckConstraint("grade >= 0 and grade <= 5"),
        UniqueConstraint(
            "housing_id",
            "review_category_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("review_category_id",),
            ("review_category.id",),
            name="fk_on_review_category",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )

    housing_id: int = Column(Integer, nullable=False)
    housing: Housing = relationship(
        "Housing", back_populates="review_grades", uselist=False
    )

    review_category_id: int = Column(Integer, nullable=False)
    review_category: ReviewCategory = relationship(
        "ReviewCategory", back_populates="review_grades", uselist=False
    )

    grade: Mapped[Union[float, Decimal, int]] = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, housing='{self.housing}', "
            f"review_category='{self.review_category}', "
            f"grade='{self.grade}')>"
        )


class User(Base, BaseMixin):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint(
            "email",
        ),
    )

    name: Optional[str] = Column(String, nullable=True)
    surname: Optional[str] = Column(String, nullable=True)

    _phone_number: Optional[str] = Column(Unicode(255), nullable=True)
    phone_country_code: Optional[str] = Column(Unicode(8), nullable=True)

    @hybrid_property
    def phone_number(self) -> Union[PhoneNumber, None]:
        return (
            PhoneNumber(self._phone_number, self.phone_country_code)
            if self._phone_number and self.phone_country_code
            else None
        )

    email: Any = Column(EmailType, nullable=False)
    birth_date: Optional[date] = Column(Date, nullable=True)
    image: Optional[str] = Column(String)
    password: str = Column(Text, nullable=False)

    # chats
    housings: List[Housing] = relationship(
        "Housing", back_populates="user", uselist=True, collection_class=list
    )
    requests: List["HousingRequest"] = relationship(
        "HousingRequest", back_populates="user", uselist=True, collection_class=list
    )
    # todo
    #: UserReview reviews = relationship('UserReview', back_populates='user')
    #: UserReview reviews_author = relationship('UserReview', back_populates='reviewer')
    history: List["HousingHistory"] = relationship(
        "HousingHistory", back_populates="user", uselist=True, collection_class=list
    )
    messages: List["ChatMessage"] = relationship(
        "ChatMessage", back_populates="user", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"surname='{self.surname}', "
            f"email='{self.email}')>"
        )


class HousingRequest(Base, BaseMixin):
    __tablename__ = "request"
    __table_args__ = (
        CheckConstraint(
            "number_of_guests > 0 and number_of_guests < 10",
            name="check_numbers_of_guests",
        ),
        UniqueConstraint(
            "housing_id",
            "user_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("user_id",),
            ("user.id",),
            name="fk_on_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    during: DateTimeRange = Column(TSRANGE(), nullable=False)
    number_of_guests: int = Column(Integer, nullable=False)
    message: str = Column(String)

    housing_id: int = Column(Integer, nullable=False)
    user_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship("Housing", back_populates="requests", uselist=False)
    user: User = relationship("User", back_populates="requests", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"housing='{self.housing}', "
            f"user='{self.user}', "
            f"number_of_guests='{self.number_of_guests}', "
            f"during='{self.during}', "
            f"message='{self.message}')>"
        )


class HousingHistory(Base, BaseMixin):
    __tablename__ = "housing_history"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
            "user_id",
        ),
        UniqueConstraint(
            "id",
            "user_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("user_id",),
            ("user.id",),
            name="fk_on_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    during: DateTimeRange = Column(TSRANGE(), nullable=False)

    housing_id: int = Column(Integer, nullable=False)
    user_id: int = Column(Integer, nullable=False)

    housing: Housing = relationship("Housing", back_populates="history", uselist=False)
    user: User = relationship("User", back_populates="history", uselist=False)
    housing_review: "HousingReview" = relationship(
        "HousingReview", back_populates="history", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"housing='{self.housing}', "
            f"user='{self.user}', "
            f"housing_reviews='{self.housing_review}', "
            f"during='{self.during}')>"
        )


class HousingReview(Base, BaseMixin):
    __tablename__ = "housing_review"
    __table_args__ = (
        UniqueConstraint(
            "history_id",
            "user_id",
        ),
        ForeignKeyConstraint(
            ("history_id", "user_id"),
            ("housing_history.id", "housing_history.user_id"),
            name="fk_on_housing_history",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    content: str = Column(String, nullable=False)

    history_id: int = Column(Integer, nullable=False)
    user_id: int = Column(Integer, nullable=False)

    history: HousingHistory = relationship(
        "HousingHistory", back_populates="housing_review", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"history='{self.history}', "
            f"content='{self.content}')>"
        )


class UserReview(Base, BaseMixin):
    __tablename__ = "user_review"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "reviewer_id",
        ),
        ForeignKeyConstraint(
            ("reviewer_id",),
            ("user.id",),
            name="fk_reviewer",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("user_id",),
            ("user.id",),
            name="fk_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    content: str = Column(String, nullable=False)

    user_id: int = Column(Integer, nullable=False)
    reviewer_id: int = Column(Integer, nullable=False)

    user: User = relationship("User", foreign_keys=[user_id], uselist=False)
    reviewer: User = relationship("User", foreign_keys=[reviewer_id], uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"user='{self.user}', "
            f"reviewer='{self.reviewer}', "
            f"content='{self.content}')>"
        )


class Chat(Base, BaseMixin):
    __tablename__ = "chat"
    __table_args__ = (
        UniqueConstraint(
            "user1_id",
            "user2_id",
        ),
        ForeignKeyConstraint(
            ("user1_id",),
            ("user.id",),
            name="fk_user1_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("user2_id",),
            ("user.id",),
            name="fk_user2_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )

    messages: List["ChatMessage"] = relationship(
        "ChatMessage", back_populates="chat", uselist=True, collection_class=list
    )

    user1_id: int = Column(Integer, nullable=False)
    user2_id: int = Column(Integer, nullable=False)

    user1: User = relationship("User", foreign_keys=[user1_id], uselist=False)
    user2: User = relationship("User", foreign_keys=[user2_id], uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"user1='{self.user1}', "
            f"user2='{self.user2}', "
            f"messages='{self.messages}')>"
        )


class ChatMessage(Base, BaseMixin):
    __tablename__ = "chat_message"
    __table_args__ = (
        UniqueConstraint(
            "message_order",
            "user_id",
            "chat_id",
        ),
        ForeignKeyConstraint(
            ("user_id",),
            ("user.id",),
            name="fk_on_user",
            ondelete="SeT NULL",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("chat_id",),
            ("chat.id",),
            name="fk_on_chat",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    content: str = Column(String, nullable=False)
    # todo it without autoincrement
    message_order: int = Column(Integer, nullable=False)

    user_id: int = Column(Integer, nullable=False)
    chat_id: int = Column(Integer, nullable=False)

    user: User = relationship("User", back_populates="messages", uselist=False)
    chat: Chat = relationship("Chat", back_populates="messages", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"chat='{self.chat}', "
            f"user='{self.user}', "
            f"content='{self.content}', "
            f"message_order='{self.message_order}')>"
        )


class ComfortCategory(Base, BaseMixin):
    __tablename__ = "comfort_category"

    name: str = Column(String(50), nullable=False)

    comforts: List["Comfort"] = relationship(
        "Comfort", back_populates="category", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, " f"name='{self.name}')>"


class Comfort(Base, BaseMixin):
    __tablename__ = "comfort"
    __table_args__ = (
        ForeignKeyConstraint(
            ("category_id",),
            ("comfort_category.id",),
            name="fk_on_category",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    name: str = Column(String(50), nullable=False)

    category_id: int = Column(Integer, nullable=False)

    category: ComfortCategory = relationship(
        "ComfortCategory", back_populates="comforts", uselist=False
    )
    housing_comforts: List["HousingComfort"] = relationship(
        "HousingComfort", back_populates="comfort", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"category='{self.category}')>"
        )


class HousingComfort(Base, BaseMixin):
    __tablename__ = "housing_comfort"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
            "comfort_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("comfort_id",),
            ("comfort.id",),
            name="fk_on_comfort",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    housing_id = Column(Integer, nullable=False)
    comfort_id = Column(Integer, nullable=False)

    housing: Housing = relationship(
        "Housing", back_populates="housing_comforts", uselist=False
    )
    comfort: Comfort = relationship(
        "Comfort", back_populates="housing_comforts", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"housing='{self.housing}', "
            f"comfort='{self.comfort}')>"
        )


class Feature(Base, BaseMixin):
    __tablename__ = "feature"

    name: str = Column(String(50), nullable=False)

    housing_features: List["HousingFeature"] = relationship(
        "HousingFeature", back_populates="feature", uselist=True, collection_class=list
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, " f"name='{self.name}')>"


class HousingFeature(Base, BaseMixin):
    __tablename__ = "housing_feature"
    __table_args__ = (
        UniqueConstraint(
            "housing_id",
            "feature_id",
        ),
        ForeignKeyConstraint(
            ("housing_id",),
            ("housing.id",),
            name="fk_on_housing",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ("feature_id",),
            ("feature.id",),
            name="fk_on_feature",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    housing_id = Column(Integer, nullable=False)
    feature_id = Column(Integer, nullable=False)

    housing: Housing = relationship(
        "Housing", back_populates="housing_features", uselist=False
    )
    feature: Feature = relationship(
        "Feature", back_populates="housing_features", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"housing='{self.housing}', "
            f"feature='{self.feature}')>"
        )
