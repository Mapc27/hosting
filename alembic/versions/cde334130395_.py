"""empty message

Revision ID: cde334130395
Revises: 125e16b35258
Create Date: 2022-06-01 16:09:08.406396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cde334130395"
down_revision = "125e16b35258"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "characteristic_type", ["name"])
    op.alter_column(
        "housing", "category_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column("housing", "type_id", existing_type=sa.INTEGER(), nullable=False)
    op.create_unique_constraint(None, "housing_category", ["name"])
    op.create_unique_constraint(None, "housing_type", ["name"])
    op.create_unique_constraint(None, "housing_type", ["description"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "housing_type", type_="unique")
    op.drop_constraint(None, "housing_type", type_="unique")
    op.drop_constraint(None, "housing_category", type_="unique")
    op.alter_column("housing", "type_id", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("housing", "category_id", existing_type=sa.INTEGER(), nullable=True)
    op.drop_constraint(None, "characteristic_type", type_="unique")
    # ### end Alembic commands ###
