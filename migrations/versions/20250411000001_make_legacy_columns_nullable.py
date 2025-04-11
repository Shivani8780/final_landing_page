"""Make legacy columns nullable

Revision ID: 20250411000001
Revises: 20250411000000
Create Date: 2025-04-11 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250411000001'
down_revision = '20250411000000'
branch_labels = None
depends_on = None


def upgrade():
    # Make legacy columns nullable
    op.alter_column('gallery_item', 'image_url', nullable=True)
    op.alter_column('gallery_item', 'youtube_url', nullable=True)

def downgrade():
    # Restore NOT NULL constraints
    op.alter_column('gallery_item', 'image_url', nullable=False)
    op.alter_column('gallery_item', 'youtube_url', nullable=False)
