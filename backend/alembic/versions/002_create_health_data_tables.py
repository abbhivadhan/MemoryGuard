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
    
    # Create enums (with IF NOT EXISTS check)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE metrictype AS ENUM ('cognitive', 'biomarker', 'imaging', 'lifestyle', 'cardiovascular');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE metricsource AS ENUM ('manual', 'assessment', 'device', 'lab');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE assessmenttype AS ENUM ('MMSE', 'MoCA', 'CDR', 'ClockDrawing');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE assessmentstatus AS ENUM ('in_progress', 'completed', 'abandoned');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE riskcategory AS ENUM ('low', 'moderate', 'high');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE relationshiptype AS ENUM ('family', 'friend', 'caregiver', 'healthcare_provider', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create health_metrics table
    op.execute("""
        CREATE TABLE health_metrics (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type metrictype NOT NULL,
            name VARCHAR NOT NULL,
            value FLOAT NOT NULL,
            unit VARCHAR NOT NULL,
            source metricsource NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            notes VARCHAR,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
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
    op.execute("""
        CREATE TABLE assessments (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type assessmenttype NOT NULL,
            status assessmentstatus NOT NULL,
            score INTEGER,
            max_score INTEGER NOT NULL,
            responses JSON NOT NULL DEFAULT '{}',
            duration INTEGER,
            started_at TIMESTAMPTZ NOT NULL,
            completed_at TIMESTAMPTZ,
            notes VARCHAR,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes for assessments
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])
    op.create_index('ix_assessments_type', 'assessments', ['type'])
    op.create_index('ix_assessments_completed_at', 'assessments', ['completed_at'])
    op.create_index('ix_assessments_user_type', 'assessments', ['user_id', 'type'])
    op.create_index('ix_assessments_user_completed', 'assessments', ['user_id', 'completed_at'])
    op.create_index('ix_assessments_user_type_completed', 'assessments', ['user_id', 'type', 'completed_at'])
    
    # Create medications table
    op.execute("""
        CREATE TABLE medications (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            dosage VARCHAR NOT NULL,
            frequency VARCHAR NOT NULL,
            schedule TIMESTAMPTZ[] NOT NULL DEFAULT '{}',
            adherence_log JSON NOT NULL DEFAULT '[]',
            side_effects VARCHAR[] NOT NULL DEFAULT '{}',
            active BOOLEAN NOT NULL DEFAULT true,
            instructions VARCHAR,
            prescriber VARCHAR,
            pharmacy VARCHAR,
            start_date TIMESTAMPTZ NOT NULL,
            end_date TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes for medications
    op.create_index('ix_medications_user_id', 'medications', ['user_id'])
    op.create_index('ix_medications_active', 'medications', ['active'])
    op.create_index('ix_medications_user_active', 'medications', ['user_id', 'active'])
    op.create_index('ix_medications_user_start_date', 'medications', ['user_id', 'start_date'])
    
    # Create predictions table
    op.execute("""
        CREATE TABLE predictions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            risk_score FLOAT NOT NULL,
            risk_category riskcategory NOT NULL,
            confidence_interval_lower FLOAT NOT NULL,
            confidence_interval_upper FLOAT NOT NULL,
            feature_importance JSON NOT NULL DEFAULT '{}',
            forecast_six_month FLOAT,
            forecast_twelve_month FLOAT,
            forecast_twenty_four_month FLOAT,
            recommendations VARCHAR[] NOT NULL DEFAULT '{}',
            model_version VARCHAR NOT NULL,
            model_type VARCHAR NOT NULL,
            input_features JSON NOT NULL DEFAULT '{}',
            prediction_date TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes for predictions
    op.create_index('ix_predictions_user_id', 'predictions', ['user_id'])
    op.create_index('ix_predictions_risk_category', 'predictions', ['risk_category'])
    op.create_index('ix_predictions_prediction_date', 'predictions', ['prediction_date'])
    op.create_index('ix_predictions_user_date', 'predictions', ['user_id', 'prediction_date'])
    op.create_index('ix_predictions_user_risk', 'predictions', ['user_id', 'risk_category'])
    
    # Create emergency_contacts table
    op.execute("""
        CREATE TABLE emergency_contacts (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            phone VARCHAR NOT NULL,
            email VARCHAR,
            relationship relationshiptype NOT NULL,
            relationship_description VARCHAR,
            priority VARCHAR NOT NULL DEFAULT '1',
            active BOOLEAN NOT NULL DEFAULT true,
            address VARCHAR,
            notes VARCHAR,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes for emergency_contacts
    op.create_index('ix_emergency_contacts_user_id', 'emergency_contacts', ['user_id'])
    op.create_index('ix_emergency_contacts_user_active', 'emergency_contacts', ['user_id', 'active'])
    op.create_index('ix_emergency_contacts_user_priority', 'emergency_contacts', ['user_id', 'priority'])
    
    # Create caregiver_relationships table
    op.execute("""
        CREATE TABLE caregiver_relationships (
            id UUID PRIMARY KEY,
            patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            caregiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            relationship_type relationshiptype NOT NULL,
            relationship_description VARCHAR,
            can_view_health_data BOOLEAN NOT NULL DEFAULT true,
            can_view_assessments BOOLEAN NOT NULL DEFAULT true,
            can_view_medications BOOLEAN NOT NULL DEFAULT true,
            can_manage_reminders BOOLEAN NOT NULL DEFAULT true,
            can_receive_alerts BOOLEAN NOT NULL DEFAULT true,
            active BOOLEAN NOT NULL DEFAULT true,
            approved BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes for caregiver_relationships
    op.create_index('ix_caregiver_relationships_patient_id', 'caregiver_relationships', ['patient_id'])
    op.create_index('ix_caregiver_relationships_caregiver_id', 'caregiver_relationships', ['caregiver_id'])
    op.create_index('ix_caregiver_relationships_active', 'caregiver_relationships', ['active'])
    op.create_index('ix_caregiver_relationships_patient_active', 'caregiver_relationships', ['patient_id', 'active'])
    op.create_index('ix_caregiver_relationships_caregiver_active', 'caregiver_relationships', ['caregiver_id', 'active'])
    op.create_index('ix_caregiver_relationships_unique', 'caregiver_relationships', ['patient_id', 'caregiver_id'], unique=True)
    
    # Create provider_relationships table
    op.execute("""
        CREATE TABLE provider_relationships (
            id UUID PRIMARY KEY,
            patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            provider_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            provider_type VARCHAR,
            specialty VARCHAR,
            organization VARCHAR,
            can_view_all_data BOOLEAN NOT NULL DEFAULT true,
            can_add_notes BOOLEAN NOT NULL DEFAULT true,
            can_view_predictions BOOLEAN NOT NULL DEFAULT true,
            active BOOLEAN NOT NULL DEFAULT true,
            approved BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
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
