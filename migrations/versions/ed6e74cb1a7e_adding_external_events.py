"""Adding external events

Revision ID: ed6e74cb1a7e
Revises: 93c749eaa6b4
Create Date: 2022-07-04 15:34:39.599457

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ed6e74cb1a7e'
down_revision = '93c749eaa6b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('external_calendar',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=128), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('url', sa.String(length=512), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('roles_users_user_id_fkey', 'roles_users', type_='foreignkey')
    op.create_foreign_key(None, 'roles_users', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roles_users', type_='foreignkey')
    op.create_foreign_key('roles_users_user_id_fkey', 'roles_users', 'old_user', ['user_id'], ['id'])
    op.drop_table('external_calendar')
    # ### end Alembic commands ###
