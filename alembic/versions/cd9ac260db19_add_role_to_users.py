"""add_role_to_users

Revision ID: cd9ac260db19
Revises: ddf58e79eebd
Create Date: 2026-01-11 18:05:47.103527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd9ac260db19'
down_revision: Union[str, Sequence[str], None] = 'ddf58e79eebd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum 타입 정의
userrole_enum = sa.Enum('MASTER', 'USER', name='userrole')


def upgrade() -> None:
    """Upgrade schema."""
    # 1. PostgreSQL Enum 타입 먼저 생성
    userrole_enum.create(op.get_bind(), checkfirst=True)
    
    # 2. 컬럼 추가 (기본값 'USER')
    op.add_column(
        'users',
        sa.Column(
            'role',
            userrole_enum,
            nullable=False,
            server_default='USER'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. 컬럼 삭제
    op.drop_column('users', 'role')
    
    # 2. Enum 타입 삭제
    userrole_enum.drop(op.get_bind(), checkfirst=True)
