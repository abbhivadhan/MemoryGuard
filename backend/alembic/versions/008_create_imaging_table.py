"""create imaging table

Revision ID: 008
Revises: 007
Create Date: 2025-11-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create imaging modality enum
    imaging_modality_enum = postgresql.ENUM(
        'MRI', 'CT', 'PET', 'SPECT',
        name='imagingmodality',
        create_type=True
    )
    imaging_modality_enum.create(op.get_bind(), checkfirst=True)
    
    # Create imaging status enum
    imaging_status_enum = postgresql.ENUM(
        'uploaded', 'processing', 'completed', 'failed',
        name='imagingstatus',
        create_type=True
    )
    imaging_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create medical_imaging table
    op.create_table(
        'medical_imaging',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # User relationship
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        
        # Imaging metadata
        sa.Column('modality', imaging_modality_enum, nullable=False),
        sa.Column('study_date', sa.String(), nullable=True),
        sa.Column('study_description', sa.String(), nullable=True),
        sa.Column('series_description', sa.String(), nullable=True),
        
        # File storage
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Float(), nullable=False),
        
        # Processing status
        sa.Column('status', imaging_status_enum, nullable=False, server_default='uploaded'),
        sa.Column('processing_error', sa.String(), nullable=True),
        
        # Volumetric measurements
        sa.Column('hippocampal_volume_left', sa.Float(), nullable=True),
        sa.Column('hippocampal_volume_right', sa.Float(), nullable=True),
        sa.Column('hippocampal_volume_total', sa.Float(), nullable=True),
        sa.Column('entorhinal_cortex_volume_left', sa.Float(), nullable=True),
        sa.Column('entorhinal_cortex_volume_right', sa.Float(), nullable=True),
        sa.Column('cortical_thickness_mean', sa.Float(), nullable=True),
        sa.Column('cortical_thickness_std', sa.Float(), nullable=True),
        sa.Column('total_brain_volume', sa.Float(), nullable=True),
        sa.Column('total_gray_matter_volume', sa.Float(), nullable=True),
        sa.Column('total_white_matter_volume', sa.Float(), nullable=True),
        sa.Column('ventricle_volume', sa.Float(), nullable=True),
        
        # Atrophy detection
        sa.Column('atrophy_detected', postgresql.JSON(), nullable=True),
        sa.Column('atrophy_severity', sa.String(), nullable=True),
        
        # Additional analysis
        sa.Column('analysis_results', postgresql.JSON(), nullable=True),
        sa.Column('ml_features', postgresql.JSON(), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_medical_imaging_user_id', 'medical_imaging', ['user_id'])
    op.create_index('ix_medical_imaging_status', 'medical_imaging', ['status'])
    op.create_index('ix_medical_imaging_created_at', 'medical_imaging', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_medical_imaging_created_at', 'medical_imaging')
    op.drop_index('ix_medical_imaging_status', 'medical_imaging')
    op.drop_index('ix_medical_imaging_user_id', 'medical_imaging')
    
    # Drop table
    op.drop_table('medical_imaging')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS imagingstatus')
    op.execute('DROP TYPE IF EXISTS imagingmodality')
