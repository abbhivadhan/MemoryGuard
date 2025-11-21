"""create memory assistant tables

Revision ID: 003
Revises: 002
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reminder_type', sa.Enum('medication', 'appointment', 'routine', 'custom', name='remindertype'), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('frequency', sa.Enum('once', 'daily', 'weekly', 'monthly', 'custom', name='reminderfrequency'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('send_notification', sa.Boolean(), nullable=False, default=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    
    # Create daily_routines table
    op.create_table(
        'daily_routines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_time', sa.Time(), nullable=True),
        sa.Column('time_of_day', sa.String(50), nullable=True),
        sa.Column('days_of_week', postgresql.ARRAY(sa.Integer()), nullable=False, default=[]),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('reminder_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_daily_routines_user_id', 'daily_routines', ['user_id'])
    
    # Create routine_completions table
    op.create_table(
        'routine_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('routine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_routine_completions_user_id', 'routine_completions', ['user_id'])
    op.create_index('ix_routine_completions_routine_id', 'routine_completions', ['routine_id'])
    op.create_index('ix_routine_completions_completion_date', 'routine_completions', ['completion_date'])
    
    # Create face_profiles table
    op.create_table(
        'face_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('relationship', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('face_embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_face_profiles_user_id', 'face_profiles', ['user_id'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('face_profiles')
    op.drop_table('routine_completions')
    op.drop_table('daily_routines')
    op.drop_table('reminders')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS remindertype')
    op.execute('DROP TYPE IF EXISTS reminderfrequency')
