"""Simplify IDs

Revision ID: 978c6c6d8e7d
Revises: d2cb72a56fbb
Create Date: 2022-09-26 01:32:10.586059-07:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '978c6c6d8e7d'
down_revision = 'd2cb72a56fbb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    ## Seeds update
    op.add_column('seeds', sa.Column('pkt_id', sa.String(length=4)))
    op.drop_constraint('_seeds_uc', 'seeds', type_='unique')
    op.create_unique_constraint('_seeds_uc', 'seeds', ['cultivar_id', 'pkt_id'])
    query = """UPDATE seeds
    SET pkt_id=SUBSTRING(CAST(year AS VARCHAR), 3, 5) || variant
    """
    op.execute(query)
    op.alter_column('seeds', 'pkt_id', nullable=False)
    op.drop_column('seeds', 'variant')

    ## Plant update
    op.add_column('plant', sa.Column('plant_id', sa.String(length=6)))
    op.drop_constraint('_plant_id_uc', 'plant', type_='unique')
    op.create_unique_constraint('_plant_id_uc', 'plant', ['plant_id'])
    query = """UPDATE plant p
    SET plant_id = s.pkt_id || LPAD(cast(p.individual AS VARCHAR), 2, '0')
    FROM seeds s
    WHERE p.seeds_id = s.id
    """
    op.execute(query)
    op.alter_column('plant', 'plant_id', nullable=False)
    op.drop_column('plant', 'individual')
    # ### end Alembic commands ###


def downgrade() -> None:
    ## Seeds update
    op.add_column('seeds', sa.Column('variant', sa.VARCHAR(length=2), autoincrement=False))
    op.drop_constraint('_seeds_uc', 'seeds', type_='unique')
    op.create_unique_constraint('_seeds_uc', 'seeds', ['cultivar_id', 'year', 'variant'])
    query = """UPDATE seeds
    SET variant=SUBSTR(pkt_id, 3)
    """
    op.execute(query)
    op.alter_column('seeds', 'variant', nullable=False)
    op.drop_column('seeds', 'pkt_id')

    ## Plant update
    op.add_column('plant', sa.Column('individual', sa.INTEGER(), autoincrement=False))
    op.drop_constraint('_plant_id_uc', 'plant', type_='unique')
    op.create_unique_constraint('_plant_id_uc', 'plant', ['seeds_id', 'individual'])
    query = """UPDATE plant
    SET individual = CAST(RIGHT(plant_id, 2) AS INT)
    """
    op.execute(query)
    op.alter_column('plant', 'individual', nullable=False)
    op.drop_column('plant', 'plant_id')
    # ### end Alembic commands ###
