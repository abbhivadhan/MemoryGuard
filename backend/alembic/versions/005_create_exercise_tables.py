"""create exercise tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create exercise_type enum
    exercise_type_enum = postgresql.ENUM(
        'memory_game', 'pattern_recognition', 'problem_solving',
        name='exercisetype',
        create_type=True
    )
    exercise_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create difficulty_level enum
    difficulty_level_enum = postgresql.ENUM(
        'easy', 'medium', 'hard', 'expert',
        name='difficultylevel',
        create_type=True
    )
    difficulty_level_enum.create(op.get_bind(), checkfirst=True)
    
    # Create exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('type', exercise_type_enum, nullable=False),
        sa.Column('difficulty', difficulty_level_enum, nullable=False),
        sa.Column('instructions', sa.String(), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercises_id'), 'exercises', ['id'], unique=False)
    
    # Create exercise_performances table
    op.create_table(
        'exercise_performances',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('exercise_id', sa.String(), nullable=False),
        sa.Column('difficulty', difficulty_level_enum, nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('time_taken', sa.Integer(), nullable=True),
        sa.Column('completed', sa.Integer(), nullable=True),
        sa.Column('performance_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercise_performances_id'), 'exercise_performances', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_exercise_performances_id'), table_name='exercise_performances')
    op.drop_table('exercise_performances')
    op.drop_index(op.f('ix_exercises_id'), table_name='exercises')
    op.drop_table('exercises')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS exercisetype')
    op.execute('DROP TYPE IF EXISTS difficultylevel')
