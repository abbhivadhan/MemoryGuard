"""create emergency tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create emergency_alerts table
    op.create_table(
        'emergency_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('latitude', sa.Float, nullable=True),
        sa.Column('longitude', sa.Float, nullable=True),
        sa.Column('location_accuracy', sa.Float, nullable=True),
        sa.Column('location_address', sa.String, nullable=True),
        sa.Column('medical_info', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('resolved_at', sa.String, nullable=True),
        sa.Column('resolution_notes', sa.String, nullable=True),
        sa.Column('contacts_notified', postgresql.JSON, nullable=True),
        sa.Column('notification_sent_at', sa.String, nullable=True),
        sa.Column('trigger_type', sa.String, nullable=False, default='manual'),
        sa.Column('notes', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_emergency_alerts_user_id', 'emergency_alerts', ['user_id'])
    op.create_index('ix_emergency_alerts_is_active', 'emergency_alerts', ['is_active'])
    op.create_index('ix_emergency_alerts_user_active', 'emergency_alerts', ['user_id', 'is_active'])
    op.create_index('ix_emergency_alerts_created', 'emergency_alerts', ['created_at'])


def downgrade():
    op.drop_index('ix_emergency_alerts_created', table_name='emergency_alerts')
    op.drop_index('ix_emergency_alerts_user_active', table_name='emergency_alerts')
    op.drop_index('ix_emergency_alerts_is_active', table_name='emergency_alerts')
    op.drop_index('ix_emergency_alerts_user_id', table_name='emergency_alerts')
    op.drop_table('emergency_alerts')
