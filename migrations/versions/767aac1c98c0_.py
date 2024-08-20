"""empty message

Revision ID: 767aac1c98c0
Revises: 
Create Date: 2024-08-11 23:23:10.645727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '767aac1c98c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('round_number', sa.Integer(), nullable=True),
    sa.Column('seasonName', sa.String(length=10), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('match_number', sa.Integer(), nullable=True),
    sa.Column('check', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teams',
    sa.Column('id', sa.String(length=4), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('owner_name', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('players',
    sa.Column('id', sa.String(length=6), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('teamid', sa.String(length=4), nullable=True),
    sa.Column('gender', sa.String(length=6), nullable=True),
    sa.ForeignKeyConstraint(['teamid'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_detail',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('gameid', sa.Integer(), nullable=True),
    sa.Column('playerid', sa.String(), nullable=True),
    sa.Column('point', sa.Integer(), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('score', sa.Numeric(precision=5, scale=1), nullable=True),
    sa.Column('same_point', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['gameid'], ['games.id'], ),
    sa.ForeignKeyConstraint(['playerid'], ['players.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('playerid', sa.String(), nullable=True),
    sa.Column('entry_year', sa.Integer(), nullable=True),
    sa.Column('leave_year', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['playerid'], ['players.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player_history')
    op.drop_table('game_detail')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('games')
    # ### end Alembic commands ###
