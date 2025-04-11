"""Add media_url and media_type columns to gallery_item

Revision ID: 10132d0c90f7
Revises: 07b04a9ca877
Create Date: 2025-04-11 15:29:28.672335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10132d0c90f7'
down_revision = '07b04a9ca877'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('media_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('media_type', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery_item', schema=None) as batch_op:
        batch_op.drop_column('media_type')
        batch_op.drop_column('media_url')

    # ### end Alembic commands ###
