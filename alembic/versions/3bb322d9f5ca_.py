"""empty message

Revision ID: 3bb322d9f5ca
Revises: 735d1d3bcaea
Create Date: 2022-05-29 23:50:27.366284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3bb322d9f5ca"
down_revision = "735d1d3bcaea"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "liked_housing",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("housing_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["housing_id"],
            ["housing.id"],
            name="fk_on_housing",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_on_user",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("housing_id", "user_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("liked_housing")
    # ### end Alembic commands ###
