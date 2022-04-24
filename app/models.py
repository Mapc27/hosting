from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey, CheckConstraint, Time, Float, \
    Unicode, Date, Text
from sqlalchemy.orm import declarative_base, relationship, composite
from sqlalchemy.dialects.postgresql import TSRANGE
from sqlalchemy_utils import PhoneNumber
from sqlalchemy_utils.types.email import EmailType


class Base(object):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


BaseModel = declarative_base(cls=Base)


class Housing(BaseModel):
    __tablename__ = 'housing'

    name = Column(String(50))
    description = Column(String(500))
    address = Column(String)
    status = Column(Boolean, default=False)
    images = Column(String)

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

    category_id = Column(Integer, ForeignKey('housing_category.id'))
    type_id = Column(Integer, ForeignKey('housing_type.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}'," \
               f" address='{self.address}')>"


class CharacteristicType(BaseModel):
    __tablename__ = 'characteristic_type'

    name = Column(String(50), nullable=False)
    characteristics = relationship("Characteristic", back_populates="characteristic_type")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', characteristics='{self.characteristics}')>"


class Characteristic(BaseModel):
    __tablename__ = 'characteristic'
    __table_args__ = (
        CheckConstraint('amount >= 0'),
    )

    housing = relationship("Housing", back_populates="characteristics")
    housing_id = Column(Integer, ForeignKey('housing.id'), nullable=False)

    characteristic_type = relationship("CharacteristicType", back_populates="characteristics")
    characteristic_type_id = Column(Integer, ForeignKey('characteristic_type.id'), nullable=False)

    amount = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}'," \
               f" characteristic_type='{self.characteristic_type}', amount='{self.amount}')>"


class HousingCategory(BaseModel):
    __tablename__ = "housing_category"
    __table_args__ = (
        CheckConstraint('level >= 0'),
        CheckConstraint('level <= 2'),
    )

    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    level = Column(Integer, default=0)

    parent = relationship("HousingCategory")
    parent_id = Column(Integer, ForeignKey('housing_category.id'), nullable=True)

    housings = relationship("Housing", back_populates="category")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}', level='{self.level}'," \
               f" parent='{self.parent}', housings='{self.housings}')>"


class HousingType(BaseModel):
    __tablename__ = "housing_type"

    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)

    housings = relationship('Housing', back_populates='type')

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', description='{self.description}')>"


class HousingCalendar(BaseModel):
    __tablename__ = "housing_calendar"
    __table_args__ = (
        CheckConstraint('min_nights >= 0'),
        CheckConstraint('max_nights >= 0'),
    )

    during = Column(TSRANGE(), nullable=False)
    min_nights = Column(Integer, nullable=False)
    max_nights = Column(Integer, nullable=False)
    notification_diff_days = Column(Integer, nullable=False)
    notification_max_time = Column(Time, nullable=False)

    housing_id = Column(Integer, ForeignKey("housing.id"))
    housing = relationship('Housing', back_populates="calendar")

    def __repr__(self):
        return f"<{self.__class__.__name__}(during='{self.during}', housing='{self.housing}')>"


class HousingPricing(BaseModel):
    __tablename__ = "housing_pricing"
    __table_args__ = (
        CheckConstraint('per_night >= 0'),
        CheckConstraint('cleaning >= 0'),
        CheckConstraint('service >= 0'),
        CheckConstraint('discount_per_week >= 0'),
        CheckConstraint('discount_per_month >= 0'),
    )

    per_night = Column(Integer, nullable=False)
    cleaning = Column(Integer, nullable=False)
    service = Column(Integer, nullable=False)
    discount_per_week = Column(Integer, nullable=False)
    discount_per_month = Column(Integer, nullable=False)

    housing_id = Column(Integer, ForeignKey("housing.id"))
    housing = relationship('Housing', back_populates="pricing")

    def __repr__(self):
        return f"<{self.__class__.__name__}(per_night='{self.per_night}', housing='{self.housing}')>"


class Rule(BaseModel):
    __tablename__ = "rule"

    name = Column(String)
    housing_rules = relationship("HousingRule", back_populates="rule")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class HousingRule(BaseModel):
    __tablename__ = "housing_rule"

    housing_id = Column(Integer, ForeignKey('housing.id'))
    housing = relationship("Housing", back_populates="housing_rules")

    rule_id = Column(Integer, ForeignKey('rule.id'))
    rule = relationship("Rule", back_populates="housing_rules")

    def __repr__(self):
        return f"<{self.__class__.__name__}(rule='{self.rule}', housing='{self.housing}')>"


class ReviewCategory(BaseModel):
    __tablename__ = "review_category"

    name = Column(String)
    review_grades = relationship("ReviewGrade", back_populates="review_category")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class ReviewGrade(BaseModel):
    __tablename__ = "review_grade"
    __table_args__ = (
        CheckConstraint('grade >= 0'),
        CheckConstraint('grade <= 5'),
    )

    housing_id = Column(Integer, ForeignKey('housing.id'))
    housing = relationship("Housing", back_populates="review_grades")

    review_category_id = Column(Integer, ForeignKey('review_category.id'))
    review_category = relationship("ReviewCategory", back_populates="review_grades")

    grade = Column(Float, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', review_category='{self.review_category}', " \
               f"grade='{self.grade}')>"


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String)
    surname = Column(String)

    _phone_number = Column(Unicode(255))
    phone_country_code = Column(Unicode(8))

    phone_number = composite(
        PhoneNumber,
        _phone_number,
        phone_country_code
    )

    email = Column(EmailType)
    birth_date = Column(Date)
    image = Column(String)
    password = Column(Text)

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


class Request(BaseModel):
    __tablename__ = "request"
    __table_args__ = (
        CheckConstraint('number_of_guests > 0'),
    )

    during = Column(TSRANGE(), nullable=False)
    number_of_guests = Column(Integer)
    message = Column(String)

    housing_id = Column(Integer, ForeignKey('housing.id'))
    housing = relationship("Housing", back_populates='requests')

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates='requests')

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', user='{self.user}'," \
               f" number_of_guests='{self.number_of_guests}', during='{self.during}', message='{self.message}')>"


class HousingHistory(BaseModel):
    __tablename__ = "housing_history"

    during = Column(TSRANGE(), nullable=False)

    housing_id = Column(Integer, ForeignKey('housing.id'))
    housing = relationship("Housing", back_populates='history')

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates='history')

    housing_reviews = relationship("HousingReview", back_populates='history')

    def __repr__(self):
        return f"<{self.__class__.__name__}(housing='{self.housing}', user='{self.user}'," \
               f" housing_reviews='{self.housing_reviews}', during='{self.during}')>"


class HousingReview(BaseModel):
    __tablename__ = "housing_review"

    content = Column(String)

    history_id = Column(Integer, ForeignKey('housing_history.id'))
    history = relationship("HousingHistory", back_populates='housing_reviews')

    def __repr__(self):
        return f"<{self.__class__.__name__}(history='{self.history}', content='{self.content}')>"


class UserReview(BaseModel):
    __tablename__ = "user_review"

    content = Column(String)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", foreign_keys=[user_id])

    reviewer_id = Column(Integer, ForeignKey('user.id'))
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<{self.__class__.__name__}(user='{self.user}', reviewer='{self.reviewer}', content='{self.content}')>"


class Chat(BaseModel):
    __tablename__ = "chat"

    messages = relationship("ChatMessage", back_populates='chat')

    user1_id = Column(Integer, ForeignKey('user.id'))
    user1 = relationship("User", foreign_keys=[user1_id])

    user2_id = Column(Integer, ForeignKey('user.id'))
    user2 = relationship("User", foreign_keys=[user2_id])

    def __repr__(self):
        return f"<{self.__class__.__name__}(user1='{self.user1}', user2='{self.user2}', messages='{self.messages}')>"


class ChatMessage(BaseModel):
    __tablename__ = "chat_message"

    content = Column(String)
    message_order = Column(Integer, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates='messages')

    chat_id = Column(Integer, ForeignKey('chat.id'))
    chat = relationship("Chat", back_populates='messages')

    def __repr__(self):
        return f"<{self.__class__.__name__}(chat='{self.chat}', user='{self.user}', content='{self.content}'," \
               f" message_order='{self.message_order}')>"
