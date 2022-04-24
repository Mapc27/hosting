from sqlalchemy import (Column, Integer, String, DateTime, func, Boolean, ForeignKey, CheckConstraint, Time, Float,
                        Unicode, Date, Text, UniqueConstraint, ForeignKeyConstraint)
from sqlalchemy.orm import declarative_base, relationship, composite
from sqlalchemy.dialects.postgresql import TSRANGE
from sqlalchemy_utils import PhoneNumber
from sqlalchemy_utils.types.email import EmailType


Base = declarative_base()


class BaseMixin(object):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Housing(Base, BaseMixin):
    __tablename__ = 'housing'
    __table_args__ = (
        ForeignKeyConstraint(
            ('category_id', ),
            ('housing_category.id', ),
            name='fk_on_housing_category'
        ),
        ForeignKeyConstraint(
            ('type_id', ),
            ('housing_type.id', ),
            name='fk_on_housing_type'
        ),
        ForeignKeyConstraint(
            ('user_id',),
            ('user.id',),
            name='fk_on_user'
        ),
    )

    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    address = Column(String, nullable=False)
    status = Column(Boolean, default=False)
    images = Column(String)

    category_id = Column(Integer)
    type_id = Column(Integer)
    user_id = Column(Integer)

    calendar = relationship("HousingCalendar", back_populates='housing', uselist=False)
    pricing = relationship("HousingPricing", back_populates='housing', uselist=False)
    category = relationship("HousingCategory", back_populates='housings')
    type = relationship("HousingType", back_populates='housings')
    housing_rules = relationship("HousingRule", back_populates="housing")
    characteristics = relationship("Characteristic", back_populates="housing")
    review_grades = relationship("ReviewGrade", back_populates="housing")
    requests = relationship("Request", back_populates="housing")
    history = relationship("HousingHistory", back_populates="housing")
    user = relationship("User", back_populates="housings")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}'," \
               f" address='{self.address}')>"


class CharacteristicType(Base, BaseMixin):
    __tablename__ = 'characteristic_type'

    name = Column(String(50), nullable=False)

    characteristics = relationship("Characteristic", back_populates="characteristic_type")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', characteristics='{self.characteristics}')>"


class Characteristic(Base, BaseMixin):
    __tablename__ = 'characteristic'
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount'),
        UniqueConstraint(
            'housing_id',
            'characteristic_type_id',
            ),
        ForeignKeyConstraint(
            ('housing_id', ),
            ('housing.id', ),
            name='fk_on_housing'
        ),
        ForeignKeyConstraint(
            ('characteristic_type_id', ),
            ('characteristic_type.id', ),
            name='fk_on_characteristic_type'
        ),
    )

    amount = Column(Integer, nullable=False, default=0)

    housing_id = Column(Integer, nullable=False)
    characteristic_type_id = Column(Integer, nullable=False)

    housing = relationship("Housing", back_populates="characteristics")
    characteristic_type = relationship("CharacteristicType", back_populates="characteristics")

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}'," \
               f" characteristic_type='{self.characteristic_type}', amount='{self.amount}')>"


class HousingCategory(Base, BaseMixin):
    __tablename__ = "housing_category"
    __table_args__ = (
        CheckConstraint('level >= 0 and level <= 2'),
        ForeignKeyConstraint(
            ('parent_id', ),
            ('housing_category.id', ),
            name='fk_on_yourself',
        ),
    )

    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

    parent_id = Column(Integer, nullable=True)

    parent = relationship("HousingCategory")
    housings = relationship("Housing", back_populates="category")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}'," \
               f" level='{self.level}', parent='{self.parent}', housings='{self.housings}')>"


class HousingType(Base, BaseMixin):
    __tablename__ = "housing_type"

    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)

    housings = relationship('Housing', back_populates='type')

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}')>"


class HousingCalendar(Base, BaseMixin):
    __tablename__ = "housing_calendar"
    __table_args__ = (
        UniqueConstraint(
            'housing_id',
        ),
        CheckConstraint(
            'min_nights >= 0 and max_nights >= 0',
            name='check_numbers_of_nights',
        ),
        ForeignKeyConstraint(
            ('housing_id', ),
            ("housing.id", ),
            name='fk_on_housing'
        ),
    )

    during = Column(TSRANGE(), nullable=False)
    min_nights = Column(Integer, nullable=False)
    max_nights = Column(Integer, nullable=False)
    notification_diff_days = Column(Integer, nullable=False)
    notification_max_time = Column(Time, nullable=False)

    housing_id = Column(Integer, nullable=False)

    housing = relationship('Housing', back_populates="calendar")

    def __repr__(self):
        return f"<{self.__class__.__name__}(during='{self.during}', housing='{self.housing}')>"


class HousingPricing(Base, BaseMixin):
    __tablename__ = "housing_pricing"
    __table_args__ = (
        UniqueConstraint(
            'housing_id',
        ),
        CheckConstraint(
            'per_night >= 0',
            name='check_per_night',
        ),
        CheckConstraint(
            'cleaning >= 0',
            name='check_cleaning',
        ),
        CheckConstraint(
            'service >= 0',
            name='check_service',
        ),
        CheckConstraint(
            'discount_per_week >= 0 and discount_per_week <= 100',
            name='check_discount_per_week',
        ),
        CheckConstraint(
            'discount_per_month >= 0 and discount_per_month <= 100',
            name='check_discount_per_month',
        ),
        ForeignKeyConstraint(
            ('housing_id',),
            ("housing.id",),
            name='fk_on_housing'
        ),
    )

    per_night = Column(Integer, nullable=False)
    cleaning = Column(Integer, nullable=False)
    service = Column(Integer, nullable=False)
    discount_per_week = Column(Integer, nullable=False)
    discount_per_month = Column(Integer, nullable=False)

    housing_id = Column(Integer, nullable=False)

    housing = relationship('Housing', back_populates="pricing")

    def __repr__(self):
        return f"<{self.__class__.__name__}(per_night='{self.per_night}', housing='{self.housing}')>"


class Rule(Base, BaseMixin):
    __tablename__ = "rule"

    name = Column(String, nullable=False)

    housing_rules = relationship("HousingRule", back_populates="rule")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class HousingRule(Base, BaseMixin):
    __tablename__ = "housing_rule"
    __table_args__ = (
        UniqueConstraint(
            'housing_id',
            'rule_id',
        ),
        ForeignKeyConstraint(
            ('housing_id',),
            ("housing.id",),
            name='fk_on_housing'
        ),
        ForeignKeyConstraint(
            ('rule_id',),
            ("rule.id",),
            name='fk_on_rule'
        ),
    )

    housing_id = Column(Integer, nullable=False)
    rule_id = Column(Integer, nullable=False)

    housing = relationship("Housing", back_populates="housing_rules")
    rule = relationship("Rule", back_populates="housing_rules")

    def __repr__(self):
        return f"<{self.__class__.__name__}(rule='{self.rule}', housing='{self.housing}')>"


class ReviewCategory(Base, BaseMixin):
    __tablename__ = "review_category"

    name = Column(String, nullable=False)

    review_grades = relationship("ReviewGrade", back_populates="review_category")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class ReviewGrade(Base, BaseMixin):
    __tablename__ = "review_grade"
    __table_args__ = (
        CheckConstraint('grade >= 0 and grade <= 5'),
        UniqueConstraint(
            'housing_id',
            'review_category_id',
        ),
        ForeignKeyConstraint(
            ('housing_id',),
            ("housing.id",),
            name='fk_on_housing'
        ),
        ForeignKeyConstraint(
            ('review_category_id',),
            ("review_category.id",),
            name='fk_on_review_category',
        ),
    )

    housing_id = Column(Integer, nullable=False)
    housing = relationship("Housing", back_populates="review_grades")

    review_category_id = Column(Integer, nullable=False)
    review_category = relationship("ReviewCategory", back_populates="review_grades")

    grade = Column(Float, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', review_category='{self.review_category}', " \
               f"grade='{self.grade}')>"


class User(Base, BaseMixin):
    __tablename__ = "user"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    _phone_number = Column(Unicode(255), nullable=False)
    phone_country_code = Column(Unicode(8), nullable=False)

    phone_number = composite(
        PhoneNumber,
        _phone_number,
        phone_country_code,
    )

    email = Column(EmailType, nullable=False)
    birth_date = Column(Date, nullable=False)
    image = Column(String)
    password = Column(Text, nullable=False)

    # chats
    housings = relationship("Housing", back_populates='user')
    requests = relationship('Request', back_populates='user')
    # reviews = relationship('UserReview', back_populates='user')
    # reviews_author = relationship('UserReview', back_populates='reviewer')
    history = relationship('HousingHistory', back_populates='user')
    messages = relationship("ChatMessage", back_populates='user')

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', surname='{self.surname}'," \
               f" phone_number='{self.phone_number}')>"


class Request(Base, BaseMixin):
    __tablename__ = "request"
    __table_args__ = (
        CheckConstraint(
            'number_of_guests > 0 and number_of_guests < 10',
            name='check_numbers_of_guests',
        ),
        UniqueConstraint(
            'housing_id',
            'user_id',
        ),
        ForeignKeyConstraint(
            ('housing_id',),
            ("housing.id",),
            name='fk_on_housing'
        ),
        ForeignKeyConstraint(
            ('user_id',),
            ("user.id",),
            name='fk_on_user'
        ),
    )

    during = Column(TSRANGE(), nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    message = Column(String)

    housing_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    housing = relationship("Housing", back_populates='requests')
    user = relationship("User", back_populates='requests')

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', user='{self.user}'," \
               f" number_of_guests='{self.number_of_guests}', during='{self.during}', message='{self.message}')>"


class HousingHistory(Base, BaseMixin):
    __tablename__ = "housing_history"
    __table_args__ = (
        UniqueConstraint(
            'housing_id',
            'user_id',
        ),
        UniqueConstraint(
            'id',
            'user_id',
        ),
        ForeignKeyConstraint(
            ('housing_id',),
            ("housing.id",),
            name='fk_on_housing'
        ),
        ForeignKeyConstraint(
            ('user_id',),
            ("user.id",),
            name='fk_on_user'
        ),
    )

    during = Column(TSRANGE(), nullable=False)

    housing_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    housing = relationship("Housing", back_populates='history')
    user = relationship("User", back_populates='history')
    housing_reviews = relationship("HousingReview", back_populates='history')

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', user='{self.user}'," \
               f" housing_reviews='{self.housing_reviews}', during='{self.during}')>"


class HousingReview(Base, BaseMixin):
    __tablename__ = "housing_review"
    __table_args__ = (
        UniqueConstraint(
            'history_id',
            'user_id',
        ),
        ForeignKeyConstraint(
            ('history_id', 'user_id'),
            ("housing_history.id", "housing_history.user_id"),
            name='fk_on_housing_history',
        ),
    )

    content = Column(String, nullable=False)

    history_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    history = relationship("HousingHistory", back_populates='housing_reviews')

    def __repr__(self):
        return f"<{self.__class__.__name__}(history='{self.history}', content='{self.content}')>"


class UserReview(Base, BaseMixin):
    __tablename__ = "user_review"
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'reviewer_id',
        ),
        ForeignKeyConstraint(
            ('reviewer_id',),
            ("user.id",),
            name='fk_reviewer',
        ),
        ForeignKeyConstraint(
            ('user_id',),
            ("user.id",),
            name='fk_user',
        ),
    )

    content = Column(String, nullable=False)

    user_id = Column(Integer, nullable=False)
    reviewer_id = Column(Integer, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<{self.__class__.__name__}(user='{self.user}', reviewer='{self.reviewer}', content='{self.content}')>"


class Chat(Base, BaseMixin):
    __tablename__ = "chat"
    __table_args__ = (
        UniqueConstraint(
            'user1_id',
            'user2_id',
        ),
        ForeignKeyConstraint(
            ('user1_id',),
            ("user.id",),
            name='fk_user1_id',
        ),
        ForeignKeyConstraint(
            ('user2_id',),
            ("user.id",),
            name='fk_user2_id',
        ),
    )

    messages = relationship("ChatMessage", back_populates='chat')

    user1_id = Column(Integer, nullable=False)
    user2_id = Column(Integer, nullable=False)

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])

    def __repr__(self):
        return f"<{self.__class__.__name__}(user1='{self.user1}', user2='{self.user2}', messages='{self.messages}')>"


class ChatMessage(Base, BaseMixin):
    __tablename__ = "chat_message"
    __table_args__ = (
        UniqueConstraint(
            'message_order',
            'user_id',
            'chat_id',
        ),
        ForeignKeyConstraint(
            ('user_id',),
            ("user.id",),
            name='fk_on_user',
        ),
        ForeignKeyConstraint(
            ('chat_id',),
            ("chat.id",),
            name='fk_on_chat',
        ),
    )

    content = Column(String, nullable=False)
    # todo it without autoincrement
    message_order = Column(Integer, nullable=False)

    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)

    user = relationship("User", back_populates='messages')
    chat = relationship("Chat", back_populates='messages')

    def __repr__(self):
        return f"<{self.__class__.__name__}(chat='{self.chat}', user='{self.user}', content='{self.content}'," \
               f" message_order='{self.message_order}')>"
