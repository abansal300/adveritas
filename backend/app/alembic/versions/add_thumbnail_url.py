"""add thumbnail_url to videos

Revision ID: add_thumbnail_url
Revises: 1feb5a72f382
Create Date: 2025-10-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_thumbnail_url'
down_revision = '1feb5a72f382'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('videos', sa.Column('thumbnail_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('videos', 'thumbnail_url')

