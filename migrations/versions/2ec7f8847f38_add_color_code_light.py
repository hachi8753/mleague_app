"""add color_code_light

Revision ID: 2ec7f8847f38
Revises: e0be8a5ddc10
Create Date: 2024-08-18 00:25:43.777148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ec7f8847f38'
down_revision = 'e0be8a5ddc10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color_code_light', sa.String(length=6), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_column('color_code_light')

    # ### end Alembic commands ###
