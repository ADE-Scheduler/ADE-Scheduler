"""fix SAWarning

Revision ID: 7e8b8d04baec
Revises: 300410acb1c7
Create Date: 2022-01-23 16:21:33.177485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7e8b8d04baec"
down_revision = "300410acb1c7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("property", "level")
    op.drop_column("property", "id")
    op.rename_table("property", "schedules_users")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("schedule_users", "property")
    op.add_column(
        "property", sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False)
    )
    op.add_column(
        "property", sa.Column("level", sa.INTEGER(), autoincrement=False, nullable=True)
    )
    # ### end Alembic commands ###
