"""Force drop NOT NULL constraint on image_url

Revision ID: 07b04a9ca877
Revises: 9bc17e5bfbcb
Create Date: 2025-04-11 12:27:08.366913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07b04a9ca877'
down_revision = '9bc17e5bfbcb'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
