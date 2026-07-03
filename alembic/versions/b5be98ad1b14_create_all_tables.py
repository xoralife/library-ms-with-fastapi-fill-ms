"""create_all_tables

Revision ID: b5be98ad1b14
Revises: 7c146d5b8536
Create Date: 2026-07-03 09:01:36.911087
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR, YEAR, DECIMAL


revision: str = 'b5be98ad1b14'
down_revision: Union[str, None] = '7c146d5b8536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'authors',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('biography', sa.Text, nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'publishers',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'categories',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('parent_id', CHAR(36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'books',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('isbn', sa.String(20), unique=True, nullable=False),
        sa.Column('barcode', sa.String(100), unique=True, nullable=True),
        sa.Column('qr_code', sa.String(500), nullable=True),
        sa.Column('author_id', CHAR(36), sa.ForeignKey('authors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('publisher_id', CHAR(36), sa.ForeignKey('publishers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category_id', CHAR(36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('language', sa.String(50), nullable=False, server_default='English'),
        sa.Column('edition', sa.String(50), nullable=True),
        sa.Column('publish_year', YEAR(4), nullable=True),
        sa.Column('page_count', sa.Integer, nullable=True),
        sa.Column('shelf_location', sa.String(100), nullable=True),
        sa.Column('total_copies', sa.Integer, nullable=False, server_default='1'),
        sa.Column('available_copies', sa.Integer, nullable=False, server_default='1'),
        sa.Column('cover_image', sa.String(500), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.Enum('available', 'unavailable', 'archived', name='bookstatus'), nullable=False, server_default='available'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'librarians',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('employee_id', sa.String(50), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('qualification', sa.String(255), nullable=True),
        sa.Column('hire_date', sa.Date, nullable=False),
        sa.Column('shift', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'students',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('student_card_number', sa.String(50), unique=True, nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('semester', sa.String(20), nullable=True),
        sa.Column('enrollment_date', sa.Date, nullable=False),
        sa.Column('graduation_year', sa.String(4), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('is_blocked', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'borrow_records',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('book_id', CHAR(36), sa.ForeignKey('books.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('student_id', CHAR(36), sa.ForeignKey('students.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('librarian_id', CHAR(36), sa.ForeignKey('librarians.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('issue_date', sa.DateTime, nullable=False),
        sa.Column('due_date', sa.DateTime, nullable=False),
        sa.Column('return_date', sa.DateTime, nullable=True),
        sa.Column('renewal_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_renewals', sa.Integer, nullable=False, server_default='2'),
        sa.Column('status', sa.Enum('borrowed', 'returned', 'overdue', 'lost', 'damaged', name='borrowstatus'), nullable=False, server_default='borrowed'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'reservations',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('book_id', CHAR(36), sa.ForeignKey('books.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('student_id', CHAR(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('reservation_date', sa.DateTime, nullable=False),
        sa.Column('expiry_date', sa.DateTime, nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'cancelled', 'expired', 'fulfilled', name='reservationstatus'), nullable=False, server_default='pending'),
        sa.Column('queue_position', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'fines',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('borrow_record_id', CHAR(36), sa.ForeignKey('borrow_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', CHAR(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('amount', DECIMAL(10, 2), nullable=False),
        sa.Column('reason', sa.Enum('overdue', 'lost', 'damaged', name='finereason'), nullable=False),
        sa.Column('is_paid', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('paid_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'payments',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('fine_id', CHAR(36), sa.ForeignKey('fines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', DECIMAL(10, 2), nullable=False),
        sa.Column('payment_method', sa.Enum('cash', 'card', 'online', name='payment_method'), nullable=False),
        sa.Column('transaction_id', sa.String(255), nullable=True),
        sa.Column('payment_date', sa.DateTime, nullable=False),
        sa.Column('received_by', CHAR(36), sa.ForeignKey('librarians.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'notifications',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('type', sa.Enum('due_reminder', 'reservation', 'fine', 'general', name='notificationtype'), nullable=False, server_default='general'),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'activity_logs',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), nullable=False, index=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', CHAR(36), nullable=True),
        sa.Column('details', sa.JSON, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'settings',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'refresh_tokens',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(500), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('is_revoked', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('settings')
    op.drop_table('activity_logs')
    op.drop_table('notifications')
    op.drop_table('payments')
    op.drop_table('fines')
    op.drop_table('reservations')
    op.drop_table('borrow_records')
    op.drop_table('students')
    op.drop_table('librarians')
    op.drop_table('books')
    op.drop_table('categories')
    op.drop_table('publishers')
    op.drop_table('authors')
    op.execute('DROP TYPE IF EXISTS bookstatus')
    op.execute('DROP TYPE IF EXISTS borrowstatus')
    op.execute('DROP TYPE IF EXISTS finereason')
    op.execute('DROP TYPE IF EXISTS reservationstatus')
    op.execute('DROP TYPE IF EXISTS notificationtype')
