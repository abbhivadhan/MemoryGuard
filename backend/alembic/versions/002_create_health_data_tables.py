"""create health data tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create health data tables"""
    
    # Create enums
    op.execute("""
        CREATE TYPE metrictype AS ENUM ('cognitive', 'biomarker', 'imaging', 'lifestyle', 'cardiovascular');
        CREATE TYPE metricsource AS ENUM ('manual', 'assessment', 'device', 'lab');
        CREATE TYPE assessmenttype AS ENUM ('MMSE', 'MoCA', 'CDR', 'ClockDrawing');
        CREATE TYPE assessmentstatus AS ENUM ('in_progress', 'completed', 'abandoned');
        CREATE TYPE riskcategory AS ENUM ('low', 'moderate', 'high');
        CREATE TYPE relationshiptype AS ENUM ('family', 'friend', 'caregiver', 'healthcare_provider', 'other');
    """)
    
    # Create health_metrics table
    op.create_table(
        'health_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum(
            'cognitive', 'biomarker', 'imaging', 'lifestyle', 'cardiovascular',
            name='metrictype'
        ), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('source', sa.Enum(
            'manual', 'assessment', 'device', 'lab',
            name='metricsource'
        ), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for health_metrics
    op.create_index('ix_health_metrics_user_id', 'health_metrics', ['user_id'])
    op.create_index('ix_health_metrics_type', 'health_metrics', ['type'])
    op.create_index('ix_health_metrics_name', 'health_metrics', ['name'])
    op.create_index('ix_health_metrics_timestamp', 'health_metrics', ['timestamp'])
    op.create_index('ix_health_metrics_user_type', 'health_metrics', ['user_id', 'type'])
    op.create_index('ix_health_metrics_user_timestamp', 'health_metrics', ['user_id', 'timestamp'])
    op.create_index('ix_health_metrics_user_type_timestamp', 'health_metrics', ['user_id', 'type', 'timestamp'])
    op.create_index('ix_health_metrics_user_name', 'health_metrics', ['user_id', 'name'])
    
    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum(
            'MMSE', 'MoCA', 'CDR', 'ClockDrawing',
            name='assessmenttype'
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'in_progress', 'completed', 'abandoned',
            name='assessmentstatus'
        ), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('responses', JSON, nullable=False, server_default='{}'),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for assessments
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])
    op.create_index('ix_assessments_type', 'assessments', ['type'])
    op.create_index('ix_assessments_completed_at', 'assessments', ['completed_at'])
    op.create_index('ix_assessments_user_type', 'assessments', ['user_id', 'type'])
    op.create_index('ix_assessments_user_completed', 'assessments', ['user_id', 'completed_at'])
    op.create_index('ix_assessments_user_type_completed', 'assessments', ['user_id', 'type', 'completed_at'])
    
    # Create medications table
    op.create_table(
        'medications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('dosage', sa.String(), nullable=False),
        sa.Column('frequency', sa.String(), nullable=False),
        sa.Column('schedule', ARRAY(sa.DateTime(timezone=True)), nullable=False, server_default='{}'),
        sa.Column('adherence_log', JSON, nullable=False, server_default='[]'),
        sa.Column('side_effects', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('instructions', sa.String(), nullable=True),
        sa.Column('prescriber', sa.String(), nullable=True),
        sa.Column('pharmacy', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for medications
    op.create_index('ix_medications_user_id', 'medications', ['user_id'])
    op.create_index('ix_medications_active', 'medications', ['active'])
    op.create_index('ix_medications_user_active', 'medications', ['user_id', 'active'])
    op.create_index('ix_medications_user_start_date', 'medications', ['user_id', 'start_date'])
    
    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_category', sa.Enum(
            'low', 'moderate', 'high',
            name='riskcategory'
        ), nullable=False),
        sa.Column('confidence_interval_lower', sa.Float(), nullable=False),
        sa.Column('confidence_interval_upper', sa.Float(), nullable=False),
        sa.Column('feature_importance', JSON, nullable=False, server_default='{}'),
        sa.Column('forecast_six_month', sa.Float(), nullable=True),
        sa.Column('forecast_twelve_month', sa.Float(), nullable=True),
        sa.Column('forecast_twenty_four_month', sa.Float(), nullable=True),
        sa.Column('recommendations', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('model_type', sa.String(), nullable=False),
        sa.Column('input_features', JSON, nullable=False, server_default='{}'),
        sa.Column('prediction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for predictions
    op.create_index('ix_predictions_user_id', 'predictions', ['user_id'])
    op.create_index('ix_predictions_risk_category', 'predictions', ['risk_category'])
    op.create_index('ix_predictions_prediction_date', 'predictions', ['prediction_date'])
    op.create_index('ix_predictions_user_date', 'predictions', ['user_id', 'prediction_date'])
    op.create_index('ix_predictions_user_risk', 'predictions', ['user_id', 'risk_category'])
    
    # Create emergency_contacts table
    op.create_table(
        'emergency_contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('relationship', sa.Enum(
            'family', 'friend', 'caregiver', 'healthcare_provider', 'other',
            name='relationshiptype'
        ), nullable=False),
        sa.Column('relationship_description', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=False, server_default='1'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for emergency_contacts
    op.create_index('ix_emergency_contacts_user_id', 'emergency_contacts', ['user_id'])
    op.create_index('ix_emergency_contacts_user_active', 'emergency_contacts', ['user_id', 'active'])
    op.create_index('ix_emergency_contacts_user_priority', 'emergency_contacts', ['user_id', 'priority'])
    
    # Create caregiver_relationships table
    op.create_table(
        'caregiver_relationships',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('caregiver_id', UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type', sa.Enum(
            'family', 'friend', 'caregiver', 'healthcare_provider', 'other',
            name='relationshiptype'
        ), nullable=False),
        sa.Column('relationship_description', sa.String(), nullable=True),
        sa.Column('can_view_health_data', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_assessments', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_medications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_manage_reminders', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_receive_alerts', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['caregiver_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for caregiver_relationships
    op.create_index('ix_caregiver_relationships_patient_id', 'caregiver_relationships', ['patient_id'])
    op.create_index('ix_caregiver_relationships_caregiver_id', 'caregiver_relationships', ['caregiver_id'])
    op.create_index('ix_caregiver_relationships_active', 'caregiver_relationships', ['active'])
    op.create_index('ix_caregiver_relationships_patient_active', 'caregiver_relationships', ['patient_id', 'active'])
    op.create_index('ix_caregiver_relationships_caregiver_active', 'caregiver_relationships', ['caregiver_id', 'active'])
    op.create_index('ix_caregiver_relationships_unique', 'caregiver_relationships', ['patient_id', 'caregiver_id'], unique=True)
    
    # Create provider_relationships table
    op.create_table(
        'provider_relationships',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_type', sa.String(), nullable=True),
        sa.Column('specialty', sa.String(), nullable=True),
        sa.Column('organization', sa.String(), nullable=True),
        sa.Column('can_view_all_data', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_add_notes', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_predictions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for provider_relationships
    op.create_index('ix_provider_relationships_patient_id', 'provider_relationships', ['patient_id'])
    op.create_index('ix_provider_relationships_provider_id', 'provider_relationships', ['provider_id'])
    op.create_index('ix_provider_relationships_active', 'provider_relationships', ['active'])
    op.create_index('ix_provider_relationships_patient_active', 'provider_relationships', ['patient_id', 'active'])
    op.create_index('ix_provider_relationships_provider_active', 'provider_relationships', ['provider_id', 'active'])
    op.create_index('ix_provider_relationships_unique', 'provider_relationships', ['patient_id', 'provider_id'], unique=True)


def downgrade() -> None:
    """Drop health data tables"""
    
    # Drop tables in reverse order
    op.drop_index('ix_provider_relationships_unique', table_name='provider_relationships')
    op.drop_index('ix_provider_relationships_provider_active', table_name='provider_relationships')
    op.drop_index('ix_provider_relationships_patient_active', table_name='provider_relationships')
    op.drop_index('ix_provider_relationships_active', table_name='provider_relationships')
    op.drop_index('ix_provider_relationships_provider_id', table_name='provider_relationships')
    op.drop_index('ix_provider_relationships_patient_id', table_name='provider_relationships')
    op.drop_table('provider_relationships')
    
    op.drop_index('ix_caregiver_relationships_unique', table_name='caregiver_relationships')
    op.drop_index('ix_caregiver_relationships_caregiver_active', table_name='caregiver_relationships')
    op.drop_index('ix_caregiver_relationships_patient_active', table_name='caregiver_relationships')
    op.drop_index('ix_caregiver_relationships_active', table_name='caregiver_relationships')
    op.drop_index('ix_caregiver_relationships_caregiver_id', table_name='caregiver_relationships')
    op.drop_index('ix_caregiver_relationships_patient_id', table_name='caregiver_relationships')
    op.drop_table('caregiver_relationships')
    
    op.drop_index('ix_emergency_contacts_user_priority', table_name='emergency_contacts')
    op.drop_index('ix_emergency_contacts_user_active', table_name='emergency_contacts')
    op.drop_index('ix_emergency_contacts_user_id', table_name='emergency_contacts')
    op.drop_table('emergency_contacts')
    
    op.drop_index('ix_predictions_user_risk', table_name='predictions')
    op.drop_index('ix_predictions_user_date', table_name='predictions')
    op.drop_index('ix_predictions_prediction_date', table_name='predictions')
    op.drop_index('ix_predictions_risk_category', table_name='predictions')
    op.drop_index('ix_predictions_user_id', table_name='predictions')
    op.drop_table('predictions')
    
    op.drop_index('ix_medications_user_start_date', table_name='medications')
    op.drop_index('ix_medications_user_active', table_name='medications')
    op.drop_index('ix_medications_active', table_name='medications')
    op.drop_index('ix_medications_user_id', table_name='medications')
    op.drop_table('medications')
    
    op.drop_index('ix_assessments_user_type_completed', table_name='assessments')
    op.drop_index('ix_assessments_user_completed', table_name='assessments')
    op.drop_index('ix_assessments_user_type', table_name='assessments')
    op.drop_index('ix_assessments_completed_at', table_name='assessments')
    op.drop_index('ix_assessments_type', table_name='assessments')
    op.drop_index('ix_assessments_user_id', table_name='assessments')
    op.drop_table('assessments')
    
    op.drop_index('ix_health_metrics_user_name', table_name='health_metrics')
    op.drop_index('ix_health_metrics_user_type_timestamp', table_name='health_metrics')
    op.drop_index('ix_health_metrics_user_timestamp', table_name='health_metrics')
    op.drop_index('ix_health_metrics_user_type', table_name='health_metrics')
    op.drop_index('ix_health_metrics_timestamp', table_name='health_metrics')
    op.drop_index('ix_health_metrics_name', table_name='health_metrics')
    op.drop_index('ix_health_metrics_type', table_name='health_metrics')
    op.drop_index('ix_health_metrics_user_id', table_name='health_metrics')
    op.drop_table('health_metrics')
    
    # Drop enums
    op.execute("""
        DROP TYPE relationshiptype;
        DROP TYPE riskcategory;
        DROP TYPE assessmentstatus;
        DROP TYPE assessmenttype;
        DROP TYPE metricsource;
        DROP TYPE metrictype;
    """)
