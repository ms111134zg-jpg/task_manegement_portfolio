"""create tables

Revision ID: d35032235df2
Revises: 
Create Date: 2026-06-14 12:27:22.355082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd35032235df2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(80), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(10), server_default='todo', nullable=False),
        sa.Column('priority', sa.SmallInteger(), server_default='3', nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='tasks_user_id_fk', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('idx_id', 'tasks', ['id'])
    op.create_index('idx_status', 'tasks', ['status'])
    op.create_index('idx_due', 'tasks', ['due_date'])
    op.create_index('idx_update', 'tasks', ['updated_at'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_update', table_name='tasks')
    op.drop_index('idx_due', table_name='tasks')
    op.drop_index('idx_status', table_name='tasks')
    op.drop_index('idx_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('users')