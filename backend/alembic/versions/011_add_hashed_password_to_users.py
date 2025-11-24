"""add hashed_password to users

Revision ID: 010
Revises: 009
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add hashed_password column to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove hashed_password column from users table
    op.drop_column('users', 'hashed_password')
