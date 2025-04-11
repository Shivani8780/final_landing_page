"""update gallery schema

Revision ID: 20250411000000
Revises: 
Create Date: 2025-04-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250411000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('gallery_item', sa.Column('media_url', sa.String(length=500)))
    op.add_column('gallery_item', sa.Column('media_type', sa.String(length=20)))
    
    # Set default values for existing data
    op.execute("UPDATE gallery_item SET media_url = image_url, media_type = 'image' WHERE image_url IS NOT NULL")
    op.execute("UPDATE gallery_item SET media_url = youtube_url, media_type = 'youtube' WHERE youtube_url IS NOT NULL")
    
    # Make columns non-nullable
    op.alter_column('gallery_item', 'media_url', nullable=False)
    op.alter_column('gallery_item', 'media_type', nullable=False)

def downgrade():
    # Remove the new columns
    op.drop_column('gallery_item', 'media_url')
    op.drop_column('gallery_item', 'media_type')
