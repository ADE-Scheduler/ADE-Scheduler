"""
use uclouvain oauth

Revision ID: 93c749eaa6b4
Revises: 7e8b8d04baec
Create Date: 2022-01-23 20:45:39.617122

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "93c749eaa6b4"
down_revision = "7e8b8d04baec"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop unnecessary fields for the migration
    op.drop_column("role", "permissions")
    op.drop_column("role", "update_datetime")
    op.drop_column("user", "update_datetime")
    op.drop_column("user", "login_count")
    op.drop_column("user", "current_login_at")
    op.drop_column("user", "current_login_ip")
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "tf_totp_secret")
    op.drop_column("user", "fs_uniquifier")
    op.drop_column("user", "username")
    op.drop_column("user", "tf_primary_method")
    op.drop_column("user", "tf_phone_number")
    op.drop_column("user", "last_login_ip")
    op.drop_column("user", "us_totp_secrets")
    op.drop_column("user", "us_phone_number")
    op.drop_column("user", "create_datetime")
    op.drop_column("user", "active")

    # Rename User -> OldUser (as well as the schedules_users table)
    op.rename_table("user", "old_user")
    op.rename_table("schedules_users", "old_schedules_users")

    # Create new User table
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fgs", sa.String(length=8), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=40), nullable=True),
        sa.Column("last_name", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column(
            "autosave",
            sa.Boolean(),
            server_default=sa.sql.expression.literal(True),
            nullable=False,
        ),
        sa.Column("last_schedule_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("fgs"),
    )

    # Create new schedules_users table
    op.create_table(
        "schedules_users",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["schedule.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("new_user")
    op.drop_table("users_schedules")

    op.rename_table("old_user", "user")
    op.rename_table("old_users_schedules", "users_schedules")
    op.add_column("user", sa.Column("active", sa.BOOLEAN(), nullable=False))
    op.add_column(
        "user",
        sa.Column(
            "create_datetime",
            sa.DATETIME(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column("us_phone_number", sa.VARCHAR(length=128), nullable=True),
    )
    op.add_column(
        "user", sa.Column("us_totp_secrets", sa.TEXT(), nullable=True)
    )
    op.add_column(
        "user", sa.Column("last_login_ip", sa.VARCHAR(length=64), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("tf_phone_number", sa.VARCHAR(length=128), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("tf_primary_method", sa.VARCHAR(length=64), nullable=True),
    )
    op.add_column(
        "user", sa.Column("username", sa.VARCHAR(length=255), nullable=True)
    )
    op.add_column(
        "user", sa.Column("confirmed_at", sa.DATETIME(), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("fs_uniquifier", sa.VARCHAR(length=64), nullable=False),
    )
    op.add_column(
        "user",
        sa.Column("tf_totp_secret", sa.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "user", sa.Column("last_login_at", sa.DATETIME(), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("current_login_ip", sa.VARCHAR(length=64), nullable=True),
    )
    op.add_column(
        "user", sa.Column("current_login_at", sa.DATETIME(), nullable=True)
    )
    op.add_column("user", sa.Column("login_count", sa.INTEGER(), nullable=True))
    op.add_column(
        "user",
        sa.Column(
            "update_datetime",
            sa.DATETIME(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.add_column(
        "role",
        sa.Column(
            "update_datetime",
            sa.DATETIME(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.add_column("role", sa.Column("permissions", sa.TEXT(), nullable=True))
    # ### end Alembic commands ###
