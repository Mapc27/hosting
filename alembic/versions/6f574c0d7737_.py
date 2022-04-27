"""empty message

Revision ID: 6f574c0d7737
Revises:
Create Date: 2022-04-24 15:36:54.504539

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6f574c0d7737"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "characteristic_type",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "housing_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.CheckConstraint("level >= 0 and level <= 2"),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["housing_category.id"], name="fk_on_yourself"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "housing_type",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "review_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rule",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("_phone_number", sa.Unicode(length=255), nullable=False),
        sa.Column("phone_country_code", sa.Unicode(length=8), nullable=False),
        sa.Column(
            "email", sqlalchemy_utils.types.email.EmailType(length=255), nullable=False
        ),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("password", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chat",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user1_id", sa.Integer(), nullable=True),
        sa.Column("user2_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user1_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user2_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "housing",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("status", sa.Boolean(), nullable=True),
        sa.Column("images", sa.String(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("type_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["housing_category.id"],
        ),
        sa.ForeignKeyConstraint(
            ["category_id"], ["housing_category.id"], name="fk_on_housing_category"
        ),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["housing_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["type_id"], ["housing_type.id"], name="fk_on_housing_type"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_on_user"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "request",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("during", postgresql.TSRANGE(), nullable=False),
        sa.Column("number_of_guests", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("number_of_guests > 0 and number_of_guests < 10"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_on_user"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id", "user_id"),
    )
    op.create_table(
        "user_review",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "characteristic",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.Column("characteristic_type_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("amount >= 0", name="check_amount"),
        sa.ForeignKeyConstraint(
            ["characteristic_type_id"],
            ["characteristic_type.id"],
            name="fk_on_characteristic_type",
        ),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "housing_id", "characteristic_type_id", name="unique_fk_columns"
        ),
    )
    op.create_table(
        "chat_message",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("message_order", sa.Integer(), autoincrement=True, nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            ["chat.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "housing_calendar",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("during", postgresql.TSRANGE(), nullable=False),
        sa.Column("min_nights", sa.Integer(), nullable=False),
        sa.Column("max_nights", sa.Integer(), nullable=False),
        sa.Column("notification_diff_days", sa.Integer(), nullable=False),
        sa.Column("notification_max_time", sa.Time(), nullable=False),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("max_nights >= 0"),
        sa.CheckConstraint("min_nights >= 0"),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id"),
    )
    op.create_table(
        "housing_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("during", postgresql.TSRANGE(), nullable=False),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_on_user"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id", "user_id"),
    )
    op.create_table(
        "housing_pricing",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("per_night", sa.Integer(), nullable=False),
        sa.Column("cleaning", sa.Integer(), nullable=False),
        sa.Column("service", sa.Integer(), nullable=False),
        sa.Column("discount_per_week", sa.Integer(), nullable=False),
        sa.Column("discount_per_month", sa.Integer(), nullable=False),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("cleaning >= 0", name="check_cleaning"),
        sa.CheckConstraint(
            "discount_per_month >= 0 and discount_per_month <= 100",
            name="check_discount_per_month",
        ),
        sa.CheckConstraint(
            "discount_per_week >= 0 and discount_per_week <= 100",
            name="check_discount_per_week",
        ),
        sa.CheckConstraint("per_night >= 0", name="check_per_night"),
        sa.CheckConstraint("service >= 0", name="check_service"),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id"),
    )
    op.create_table(
        "housing_rule",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.ForeignKeyConstraint(["rule_id"], ["rule.id"], name="fk_on_rule"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id", "rule_id"),
    )
    op.create_table(
        "review_grade",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.Column("review_category_id", sa.Integer(), nullable=False),
        sa.Column("grade", sa.Float(), nullable=False),
        sa.CheckConstraint("grade >= 0 and grade <= 5"),
        sa.ForeignKeyConstraint(["housing_id"], ["housing.id"], name="fk_on_housing"),
        sa.ForeignKeyConstraint(
            ["review_category_id"], ["review_category.id"], name="fk_on_review_category"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id", "review_category_id"),
    )
    op.create_table(
        "housing_review",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("history_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["history_id"],
            ["housing_history.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("housing_review")
    op.drop_table("review_grade")
    op.drop_table("housing_rule")
    op.drop_table("housing_pricing")
    op.drop_table("housing_history")
    op.drop_table("housing_calendar")
    op.drop_table("chat_message")
    op.drop_table("characteristic")
    op.drop_table("user_review")
    op.drop_table("request")
    op.drop_table("housing")
    op.drop_table("chat")
    op.drop_table("user")
    op.drop_table("rule")
    op.drop_table("review_category")
    op.drop_table("housing_type")
    op.drop_table("housing_category")
    op.drop_table("characteristic_type")
    # ### end Alembic commands ###
