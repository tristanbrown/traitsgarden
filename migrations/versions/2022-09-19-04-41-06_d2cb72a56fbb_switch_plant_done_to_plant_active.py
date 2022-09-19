"""Switch 'plant done' to 'plant active'

Revision ID: d2cb72a56fbb
Revises: 425d6802e65c
Create Date: 2022-09-19 04:41:06.272400-07:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2cb72a56fbb'
down_revision = '425d6802e65c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('plant', 'done', new_column_name='active')

def downgrade() -> None:
    op.alter_column('plant', 'active', new_column_name='done')
