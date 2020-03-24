"""empty message

Revision ID: a5d1f8c0e986
Revises: d954a661bdf2
Create Date: 2019-11-19 23:26:56.650634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5d1f8c0e986'
down_revision = 'd954a661bdf2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles_functions',
    sa.Column('role_id', sa.String(length=32), nullable=False),
    sa.Column('function_id', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['function_id'], ['functions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'function_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_functions')
    # ### end Alembic commands ###