"""Seeds parents to Many-to-Many

Revision ID: da27694a40e2
Revises: 5f57ea426e0b
Create Date: 2022-12-18 04:09:57.145982-08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da27694a40e2'
down_revision = '5f57ea426e0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('seedparent',
        sa.Column('seeds_id', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('mother', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plant.id'], ),
        sa.ForeignKeyConstraint(['seeds_id'], ['seeds.id'], ),
        sa.PrimaryKeyConstraint('seeds_id', 'plant_id')
    )
    op.drop_constraint('seeds_mother_id_fkey', 'seeds', type_='foreignkey')
    op.drop_constraint('seeds_father_id_fkey', 'seeds', type_='foreignkey')
    op.drop_column('seeds', 'mother_id')
    op.drop_column('seeds', 'father_id')


def downgrade() -> None:
    op.add_column('seeds', sa.Column('father_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('seeds', sa.Column('mother_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('seeds_father_id_fkey', 'seeds', 'plant', ['father_id'], ['id'])
    op.create_foreign_key('seeds_mother_id_fkey', 'seeds', 'plant', ['mother_id'], ['id'])
    op.drop_table('seedparent')
