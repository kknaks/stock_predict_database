"""add_password_hash

Revision ID: 1b58beac5c63
Revises: cd9ac260db19
Create Date: 2026-01-11 18:44:23.748151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b58beac5c63'
down_revision: Union[str, Sequence[str], None] = 'cd9ac260db19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 기본 비밀번호 해시 (SHA-256 of "changeme")
# hashlib.sha256("changeme".encode()).hexdigest()
DEFAULT_PASSWORD_HASH = "057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86"


def upgrade() -> None:
    """Upgrade schema."""
    # 1. nullable=True로 컬럼 추가
    op.add_column('users', sa.Column('password_hash', sa.String(length=64), nullable=True))
    
    # 2. 기존 데이터에 기본값 설정
    op.execute(f"UPDATE users SET password_hash = '{DEFAULT_PASSWORD_HASH}' WHERE password_hash IS NULL")
    
    # 3. nullable=False로 변경
    op.alter_column('users', 'password_hash', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'password_hash')
