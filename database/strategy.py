import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

class StrategyInfo(Base, TimestampMixin):
    __tablename__ = "strategy_info"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    user_strategy: Mapped["UserStrategy"] = relationship(
        "UserStrategy",
        back_populates="strategy_info",
        uselist=False,
    )


class UserStrategy(Base, TimestampMixin):
    __tablename__ = "user_strategy"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.uid"),
        nullable=False,
    )

    strategy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("strategy_info.id"),
        nullable=False,
    )

    ls_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    tp_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    
    strategy_info: Mapped["StrategyInfo"] = relationship(
        "StrategyInfo",
        back_populates="user_strategy",
        uselist=False,
    )

    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="user_strategy",
    )