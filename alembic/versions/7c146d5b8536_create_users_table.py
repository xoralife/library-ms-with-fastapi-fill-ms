"""create_users_table

Revision ID: 7c146d5b8536
Revises: 
Create Date: 2026-07-03 08:53:54.076018
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '7c146d5b8536'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column(
            'role',
            sa.Enum('admin', 'librarian', 'student', name='userrole'),
            nullable=False,
            server_default='student',
        ),
        sa.Column('is_active', sa.Boolean(), default=True, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), default=False, server_default='0'),
        sa.Column('profile_image', sa.String(500), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
