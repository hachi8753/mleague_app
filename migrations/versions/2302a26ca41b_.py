"""empty message

Revision ID: 2302a26ca41b
Revises: 6d640dea0d0a
Create Date: 2024-08-13 15:52:12.167269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2302a26ca41b'
down_revision = '6d640dea0d0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round_detail', schema=None) as batch_op:
        batch_op.add_column(sa.Column('balance', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round_detail', schema=None) as batch_op:
        batch_op.drop_column('balance')

    # ### end Alembic commands ###
