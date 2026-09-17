"""Add roles table (1:1 with users)

Revision ID: a1b2c3d4e5f6
Revises: 6d62029bb66e
Create Date: 2026-09-14 00:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "6d62029bb66e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roles table (Rol 1:1 User)
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_roles_user_id"), "roles", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop roles table
    op.drop_index(op.f("ix_roles_user_id"), table_name="roles")
    op.drop_table("roles")
