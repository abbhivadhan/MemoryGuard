"""create recommendation tables

Revision ID: 006
Revises: 005
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.Enum('diet', 'exercise', 'sleep', 'cognitive', 'social', name='recommendationcategory'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='recommendationpriority'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('research_citations', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('evidence_strength', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('adherence_score', sa.Float(), nullable=True),
        sa.Column('generated_from_risk_factors', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('target_metrics', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    
    # Create indexes
    op.create_index('ix_recommendations_user_id', 'recommendations', ['user_id'])
    op.create_index('ix_recommendations_category', 'recommendations', ['category'])
    op.create_index('ix_recommendations_generated_at', 'recommendations', ['generated_at'])
    op.create_index('ix_recommendations_user_category', 'recommendations', ['user_id', 'category'])
    op.create_index('ix_recommendations_user_active', 'recommendations', ['user_id', 'is_active'])
    
    # Create recommendation_adherence table
    op.create_table(
        'recommendation_adherence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('outcome_metrics', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    
    # Create indexes
    op.create_index('ix_adherence_recommendation_id', 'recommendation_adherence', ['recommendation_id'])
    op.create_index('ix_adherence_user_id', 'recommendation_adherence', ['user_id'])
    op.create_index('ix_adherence_date', 'recommendation_adherence', ['date'])
    op.create_index('ix_adherence_recommendation_date', 'recommendation_adherence', ['recommendation_id', 'date'])
    op.create_index('ix_adherence_user_date', 'recommendation_adherence', ['user_id', 'date'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('recommendation_adherence')
    op.drop_table('recommendations')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS recommendationcategory')
    op.execute('DROP TYPE IF EXISTS recommendationpriority')
