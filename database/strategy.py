import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Float, String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

class StrategyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"

class WeightType(str, enum.Enum):
    EQUAL = "equal"
    MARKETCAP = "marketcap"
    VOLUME = "volume"
    PRICE = "price"

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

    user_strategies: Mapped[List["UserStrategy"]] = relationship(
        "UserStrategy",
        back_populates="strategy_info",
    )

class StrategyWeightType(Base, TimestampMixin):
    __tablename__ = "strategy_weight"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    weight_type: Mapped[WeightType] = mapped_column(
        Enum(WeightType),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship: 1:N (StrategyWeightType : UserStrategy)
    user_strategies: Mapped[List["UserStrategy"]] = relationship(
        "UserStrategy",
        back_populates="strategy_weight_type",
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

    investment_weight: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        default=0.9,
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

    is_auto: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
    )

    weight_type_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("strategy_weight.id"),
        nullable=True,
    )

    status: Mapped[StrategyStatus] = mapped_column(
        Enum(StrategyStatus),
        nullable=True,
        default=StrategyStatus.ACTIVE,
    )

    strategy_info: Mapped["StrategyInfo"] = relationship(
        "StrategyInfo",
        back_populates="user_strategies",
        uselist=False,
    )

    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="user_strategy",
    )

    strategy_weight_type: Mapped[Optional["StrategyWeightType"]] = relationship(
        "StrategyWeightType",
        back_populates="user_strategies",
        uselist=False,
    )

    # Relationship: 1:N (UserStrategy : DailyStrategy)
    daily_strategies: Mapped[List["DailyStrategy"]] = relationship(
        "DailyStrategy",
        back_populates="user_strategy",
        cascade="all, delete-orphan",
    )


class DailyStrategy(Base, TimestampMixin):
    __tablename__ = "daily_strategy"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_strategy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_strategy.id"),
        nullable=False,
    )

    buy_amount: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    sell_amount: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    total_profit_rate: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    total_profit_amount: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationship: N:1 (DailyStrategy : UserStrategy)
    user_strategy: Mapped["UserStrategy"] = relationship(
        "UserStrategy",
        back_populates="daily_strategies",
    )

    # Relationship: 1:N (DailyStrategy : DailyStrategyStock)
    stocks: Mapped[List["DailyStrategyStock"]] = relationship(
        "DailyStrategyStock",
        back_populates="daily_strategy",
        cascade="all, delete-orphan",
    )

class DailyStrategyStock(Base, TimestampMixin):
    __tablename__ = "daily_strategy_stock"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    daily_strategy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("daily_strategy.id", ondelete="CASCADE"),
        nullable=False,
    )

    stock_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    stock_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    exchange: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    stock_open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    target_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    target_quantity: Mapped[Optional[float]] = mapped_column(
        Integer,
        nullable=True,
    )

    sell_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    stop_loss_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 실제 거래 정보 (장 마감 후 업데이트)
    buy_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    buy_quantity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    sell_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    sell_quantity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    profit_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Relationship: N:1 (DailyStrategyStock : DailyStrategy)
    daily_strategy: Mapped["DailyStrategy"] = relationship(
        "DailyStrategy",
        back_populates="stocks",
    )

    # Relationship: 1:N (DailyStrategyStock : Order)
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="daily_strategy_stock",
        cascade="all, delete-orphan",
    )


class OrderStatus(str, enum.Enum):
    """주문 상태"""
    ORDERED = "ordered"  # 주문 접수
    PARTIALLY_EXECUTED = "partially_executed"  # 부분 체결
    EXECUTED = "executed"  # 전량 체결
    CANCELLED = "cancelled"  # 취소
    REJECTED = "rejected"  # 거부


class OrderType(str, enum.Enum):
    """주문 유형"""
    BUY = "BUY"
    SELL = "SELL"


class Order(Base, TimestampMixin):
    """주문 내역 테이블"""
    
    __tablename__ = "order"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    daily_strategy_stock_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("daily_strategy_stock.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    order_no: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,  # 주문번호로 빠른 조회
    )
    
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType),
        nullable=False,
    )
    
    order_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    order_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    order_dvsn: Mapped[str] = mapped_column(
        String(10),  # 00: 지정가, 01: 시장가 등
        nullable=False,
    )
    
    account_no: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
    is_mock: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.ORDERED,
    )
    
    # 누적 체결 정보 (최신 상태)
    total_executed_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    total_executed_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    
    remaining_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    is_fully_executed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    # 주문 시각
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Relationship: N:1 (Order : DailyStrategyStock)
    daily_strategy_stock: Mapped["DailyStrategyStock"] = relationship(
        "DailyStrategyStock",
        back_populates="orders",
    )
    
    # Relationship: 1:N (Order : OrderExecution)
    executions: Mapped[List["OrderExecution"]] = relationship(
        "OrderExecution",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderExecution.execution_sequence",
    )


class OrderExecution(Base, TimestampMixin):
    """체결통보 내역 테이블 (건별)"""
    
    __tablename__ = "order_execution"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("order.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 체결 순서 (같은 주문 내에서 체결 순서)
    execution_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    # 이번 체결 정보
    executed_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    executed_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    # 체결 시점의 누적 정보
    total_executed_quantity_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    total_executed_price_after: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    remaining_quantity_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    is_fully_executed_after: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    # 체결 시각
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Relationship: N:1 (OrderExecution : Order)
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="executions",
    )