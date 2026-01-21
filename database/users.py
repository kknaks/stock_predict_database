"""
User & Account 모델

사용자 정보 및 주식 계좌 관리
"""

import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .strategy import UserStrategy

class UserRole(str, enum.Enum):
    """사용자 역할"""
    MASTER = "master"  # 관리자: 모든 권한
    USER = "user"      # 일반 사용자: 제한된 권한
    MOCK = "mock"      # 모의 사용자: 모의 거래

class AccountType(str, enum.Enum):
    """계좌 유형"""
    REAL = "real"      # 한국투자증권
    PAPER = "paper"      # 모의 거래
    MOCK = "mock"      # 테스트 거래
class Users(Base, TimestampMixin):
    """사용자 테이블"""
    
    __tablename__ = "users"
    
    # Primary Key - Auto Increment
    uid: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    # 로그인 정보
    nickname: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(64),  # SHA-256 = 64자 hex
        nullable=False,
    )
    
    # 역할 (RBAC)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER,
    )
    
    # JWT 토큰
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 관계: 유저 1명 → 계좌 여러개
    accounts: Mapped[List["Accounts"]] = relationship(
        "Accounts",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    user_strategy: Mapped[List["UserStrategy"]] = relationship(
        "UserStrategy",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(uid={self.uid}, nickname='{self.nickname}')>"


class Accounts(Base, TimestampMixin):
    """주식 계좌 테이블"""
    
    __tablename__ = "stock_accounts"

    # Primary Key - Auto Increment
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    # Foreign Key - 유저 연결
    user_uid: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False,
    )

    account_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType),
        nullable=False,
        default=AccountType.REAL,
    )

    hts_id: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
    )
    
    # 계좌 정보
    account_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    
    account_balance: Mapped[float] = mapped_column(
        Numeric(20, 2),  # 소수점 2자리까지
        nullable=False,
        default=0,
    )
    
    # 한국투자증권 API 키
    app_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    app_secret: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    
    # 한국투자증권 Access Token (캐싱)
    kis_access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    kis_token_expired_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 관계: 계좌 → 유저
    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="accounts",
    )
    
    def is_token_valid(self) -> bool:
        """토큰이 유효한지 확인 (만료 5분 전까지 유효)"""
        if not self.kis_access_token or not self.kis_token_expired_at:
            return False
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        return self.kis_token_expired_at > now + timedelta(minutes=5)
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, account_number='{self.account_number}')>"
