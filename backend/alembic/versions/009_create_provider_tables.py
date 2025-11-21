"""create provider tables

Revision ID: 009
Revises: 008
Create Date: 2025-11-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create provider-related tables"""
    
    # Create provider types enum
    op.execute("""
        CREATE TYPE providertype AS ENUM (
            'physician', 'neurologist', 'psychiatrist', 
            'nurse', 'therapist', 'researcher', 'other'
        )
    """)
    
    # Create access status enum
    op.execute("""
        CREATE TYPE accessstatus AS ENUM (
            'pending', 'active', 'revoked', 'expired'
        )
    """)
    
    # Create providers table
    op.create_table(
        'providers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('google_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('picture', sa.String(), nullable=True),
        sa.Column('provider_type', sa.Enum(
            'physician', 'neurologist', 'psychiatrist', 
            'nurse', 'therapist', 'researcher', 'other',
            name='providertype'
        ), nullable=False),
        sa.Column('license_number', sa.String(), nullable=True),
        sa.Column('institution', sa.String(), nullable=True),
        sa.Column('specialty', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for providers
    op.create_index('ix_providers_email', 'providers', ['email'], unique=True)
    op.create_index('ix_providers_google_id', 'providers', ['google_id'], unique=True)
    
    # Create provider_accesses table
    op.create_table(
        'provider_accesses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum(
            'pending', 'active', 'revoked', 'expired',
            name='accessstatus'
        ), nullable=False, server_default='pending'),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('can_view_assessments', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_health_metrics', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_medications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_imaging', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_add_notes', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('granted_by_patient', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('access_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for provider_accesses
    op.create_index('ix_provider_accesses_patient_id', 'provider_accesses', ['patient_id'])
    op.create_index('ix_provider_accesses_provider_id', 'provider_accesses', ['provider_id'])
    
    # Create provider_access_logs table
    op.create_table(
        'provider_access_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('provider_access_id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_access_id'], ['provider_accesses.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for provider_access_logs
    op.create_index('ix_provider_access_logs_provider_access_id', 'provider_access_logs', ['provider_access_id'])
    op.create_index('ix_provider_access_logs_created_at', 'provider_access_logs', ['created_at'])
    
    # Create clinical_notes table
    op.create_table(
        'clinical_notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for clinical_notes
    op.create_index('ix_clinical_notes_patient_id', 'clinical_notes', ['patient_id'])
    op.create_index('ix_clinical_notes_provider_id', 'clinical_notes', ['provider_id'])


def downgrade() -> None:
    """Drop provider-related tables"""
    op.drop_index('ix_clinical_notes_provider_id', table_name='clinical_notes')
    op.drop_index('ix_clinical_notes_patient_id', table_name='clinical_notes')
    op.drop_table('clinical_notes')
    
    op.drop_index('ix_provider_access_logs_created_at', table_name='provider_access_logs')
    op.drop_index('ix_provider_access_logs_provider_access_id', table_name='provider_access_logs')
    op.drop_table('provider_access_logs')
    
    op.drop_index('ix_provider_accesses_provider_id', table_name='provider_accesses')
    op.drop_index('ix_provider_accesses_patient_id', table_name='provider_accesses')
    op.drop_table('provider_accesses')
    
    op.drop_index('ix_providers_google_id', table_name='providers')
    op.drop_index('ix_providers_email', table_name='providers')
    op.drop_table('providers')
    
    op.execute('DROP TYPE accessstatus')
    op.execute('DROP TYPE providertype')
