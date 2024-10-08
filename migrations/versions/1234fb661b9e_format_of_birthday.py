"""format of birthday

Revision ID: 1234fb661b9e
Revises: a9a28c631fb0
Create Date: 2024-08-12 00:20:31.702010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234fb661b9e'
down_revision = 'a9a28c631fb0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.alter_column('birthday',
               existing_type=sa.DATE(),
               type_=sa.String(length=6),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.alter_column('birthday',
               existing_type=sa.String(length=6),
               type_=sa.DATE(),
               existing_nullable=True)

    # ### end Alembic commands ###
