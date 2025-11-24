"""increase photo_url length for base64 images

Revision ID: 010
Revises: 009
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # Change photo_url from VARCHAR(500) to TEXT to support base64 images
    op.alter_column('face_profiles', 'photo_url',
                    existing_type=sa.String(500),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade():
    # Revert back to VARCHAR(500)
    op.alter_column('face_profiles', 'photo_url',
                    existing_type=sa.Text(),
                    type_=sa.String(500),
                    existing_nullable=True)
