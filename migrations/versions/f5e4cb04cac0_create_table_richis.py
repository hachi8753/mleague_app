"""create table richis

Revision ID: f5e4cb04cac0
Revises: 357c11add771
Create Date: 2024-08-18 15:04:50.216057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e4cb04cac0'
down_revision = '357c11add771'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('richis',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('round_id', sa.String(length=8), nullable=True),
    sa.Column('player_index', sa.String(length=2), nullable=True),
    sa.Column('turn', sa.Integer(), nullable=True),
    sa.Column('dora_pai', sa.Text(), nullable=True),
    sa.Column('richi_pai', sa.String(), nullable=True),
    sa.Column('sensei', sa.Integer(), nullable=True),
    sa.Column('machi', sa.Text(), nullable=True),
    sa.Column('tehai', sa.Text(), nullable=True),
    sa.Column('deal_in', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['player_index'], ['round_detail.player_index'], ),
    sa.ForeignKeyConstraint(['round_id'], ['rounds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('richis')
    # ### end Alembic commands ###
