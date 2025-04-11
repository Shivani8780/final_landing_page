"""Fix NULL constraints on gallery_item columns

Revision ID: 9bc17e5bfbcb
Revises: d2013be24b70
Create Date: 2025-04-11 12:12:54.064239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bc17e5bfbcb'
down_revision = 'd2013be24b70'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
