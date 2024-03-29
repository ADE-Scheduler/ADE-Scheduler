"""Adding description to external events

Revision ID: edca2de88864
Revises: ed6e74cb1a7e
Create Date: 2022-08-16 14:46:53.683176

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "edca2de88864"
down_revision = "ed6e74cb1a7e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "external_calendar",
        sa.Column("description", sa.String(length=4096), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("external_calendar", "description")
    # ### end Alembic commands ###
