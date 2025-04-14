"""fix gallery captions

Revision ID: 20250412000000
Revises: 7d1bbd9e98af
Create Date: 2025-04-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250412000000'
down_revision = '7d1bbd9e98af'
branch_labels = None
depends_on = None

def upgrade():
    # Update all "-" or empty captions to NULL
    op.execute("""
        UPDATE gallery_item 
        SET caption = NULL 
        WHERE caption = '-' OR caption = '' OR caption IS NULL
    """)

def downgrade():
    # No need to revert as we're just cleaning data
    pass
