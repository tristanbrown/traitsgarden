"""Expand generation label

Revision ID: c8d590c8a4a1
Revises: 8682451f5cbb
Create Date: 2022-12-12 03:33:28.080424-08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8d590c8a4a1'
down_revision = '8682451f5cbb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('seeds', 'generation',
        existing_type=sa.String(length=2),
        type_=sa.String(length=4)
    )


def downgrade() -> None:
    op.alter_column('seeds', 'generation',
        existing_type=sa.String(length=4),
        type_=sa.String(length=2)
    )
