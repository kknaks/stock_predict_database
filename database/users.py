"""
User & Account 모델

사용자 정보 및 주식 계좌 관리
"""

from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin


class Users(Base, TimestampMixin):
    """사용자 테이블"""
    
    __tablename__ = "users"
    
    # Primary Key - Auto Increment
    uid: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    # 사용자 정보
    nickname: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
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
    
    # 관계: 계좌 → 유저
    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="accounts",
    )
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, account_number='{self.account_number}')>"
