"""Add current_role, preferred_location, and skills to User

Revision ID: 4495102aa53f
Revises: bd9cef52a009
Create Date: 2025-05-12 10:46:06.809491

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4495102aa53f'
down_revision = 'bd9cef52a009'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_role', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preferred_location', sa.String(length=100), nullable=True))
        batch_op.alter_column('skills',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('skills',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.drop_column('preferred_location')
        batch_op.drop_column('current_role')

    # ### end Alembic commands ###
