"""add strategy_id back

Revision ID: 8780debdacfd
Revises: 688f004ca1b3
Create Date: 2026-01-15 18:59:57.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8780debdacfd'
down_revision: Union[str, Sequence[str], None] = '688f004ca1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 먼저 nullable로 컬럼 추가
    op.add_column('user_strategy', sa.Column('strategy_id', sa.BigInteger(), nullable=True))
    
    # 기존 데이터의 strategy_id를 1로 설정
    op.execute("UPDATE user_strategy SET strategy_id = 1 WHERE strategy_id IS NULL")
    
    # NOT NULL 제약조건 추가
    op.alter_column('user_strategy', 'strategy_id', nullable=False)
    
    # ForeignKey 제약조건 추가
    op.create_foreign_key(
        op.f('user_strategy_strategy_id_fkey'),
        'user_strategy',
        'strategy_info',
        ['strategy_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ForeignKey 제약조건 제거
    op.drop_constraint(op.f('user_strategy_strategy_id_fkey'), 'user_strategy', type_='foreignkey')
    
    # 컬럼 제거
    op.drop_column('user_strategy', 'strategy_id')
