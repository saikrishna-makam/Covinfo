"""empty message

Revision ID: 177210a67104
Revises: ca165ee4bfe4
Create Date: 2021-06-15 16:35:15.808197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '177210a67104'
down_revision = 'ca165ee4bfe4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    # ### end Alembic commands ###
