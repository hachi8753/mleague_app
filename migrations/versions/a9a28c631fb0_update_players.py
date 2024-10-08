"""update players

Revision ID: a9a28c631fb0
Revises: 767aac1c98c0
Create Date: 2024-08-12 00:07:18.957346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9a28c631fb0'
down_revision = '767aac1c98c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.add_column(sa.Column('organization', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('birthyear', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('birthday', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('hometown', sa.String(length=8), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.drop_column('hometown')
        batch_op.drop_column('birthday')
        batch_op.drop_column('birthyear')
        batch_op.drop_column('organization')

    # ### end Alembic commands ###
