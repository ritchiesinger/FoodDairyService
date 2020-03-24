"""empty message

Revision ID: 4ae0173836f8
Revises: 
Create Date: 2019-11-19 22:25:17.745762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ae0173836f8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('email', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('email', 'user', ['email'], unique=True)
    # ### end Alembic commands ###