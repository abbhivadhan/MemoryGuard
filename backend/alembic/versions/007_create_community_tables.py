"""create community tables

Revision ID: 007
Revises: 006
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    post_category_enum = ENUM(
        'general', 'support', 'tips', 'questions', 'resources',
        name='postcategory',
        create_type=True
    )
    post_visibility_enum = ENUM(
        'public', 'members_only', 'matched_users',
        name='postvisibility',
        create_type=True
    )
    
    # Create community_posts table
    op.create_table(
        'community_posts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', post_category_enum, nullable=False),
        sa.Column('visibility', post_visibility_enum, nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), default=False),
        sa.Column('is_flagged', sa.Boolean(), default=False),
        sa.Column('is_moderated', sa.Boolean(), default=False),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_community_posts_id', 'community_posts', ['id'])
    op.create_index('ix_community_posts_user_id', 'community_posts', ['user_id'])
    op.create_index('ix_community_posts_category', 'community_posts', ['category'])
    op.create_index('ix_community_posts_created_at', 'community_posts', ['created_at'])
    
    # Create community_replies table
    op.create_table(
        'community_replies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), default=False),
        sa.Column('is_flagged', sa.Boolean(), default=False),
        sa.Column('is_moderated', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_community_replies_id', 'community_replies', ['id'])
    op.create_index('ix_community_replies_post_id', 'community_replies', ['post_id'])
    op.create_index('ix_community_replies_user_id', 'community_replies', ['user_id'])
    
    # Create content_flags table
    op.create_table(
        'content_flags',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=True),
        sa.Column('reply_id', sa.String(), nullable=True),
        sa.Column('reporter_user_id', sa.String(), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_id'], ['community_replies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reporter_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_content_flags_id', 'content_flags', ['id'])
    op.create_index('ix_content_flags_status', 'content_flags', ['status'])
    
    # Create educational_resources table
    op.create_table(
        'educational_resources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_educational_resources_id', 'educational_resources', ['id'])
    op.create_index('ix_educational_resources_type', 'educational_resources', ['resource_type'])
    op.create_index('ix_educational_resources_featured', 'educational_resources', ['is_featured'])


def downgrade() -> None:
    op.drop_index('ix_educational_resources_featured', 'educational_resources')
    op.drop_index('ix_educational_resources_type', 'educational_resources')
    op.drop_index('ix_educational_resources_id', 'educational_resources')
    op.drop_table('educational_resources')
    
    op.drop_index('ix_content_flags_status', 'content_flags')
    op.drop_index('ix_content_flags_id', 'content_flags')
    op.drop_table('content_flags')
    
    op.drop_index('ix_community_replies_user_id', 'community_replies')
    op.drop_index('ix_community_replies_post_id', 'community_replies')
    op.drop_index('ix_community_replies_id', 'community_replies')
    op.drop_table('community_replies')
    
    op.drop_index('ix_community_posts_created_at', 'community_posts')
    op.drop_index('ix_community_posts_category', 'community_posts')
    op.drop_index('ix_community_posts_user_id', 'community_posts')
    op.drop_index('ix_community_posts_id', 'community_posts')
    op.drop_table('community_posts')
    
    # Drop enums
    ENUM(name='postvisibility').drop(op.get_bind(), checkfirst=True)
    ENUM(name='postcategory').drop(op.get_bind(), checkfirst=True)
