import enum
from datetime import datetime, date, time
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Date, Time, Enum, ForeignKey, Float, String, Text, Boolean, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .stocks import Exchange

class StrategyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"

class WeightType(str, enum.Enum):
    EQUAL = "equal"
    MARKETCAP = "marketcap"
    VOLUME = "volume"
    PRICE = "price"

class SignalType(str, enum.Enum):
    """매매 신호"""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class ConfidenceLevel(str, enum.Enum):
    """신뢰도"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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

    # Relationship: 1:N (StrategyInfo : GapPredictions)
    gap_predictions: Mapped[List["GapPredictions"]] = relationship(
        "GapPredictions",
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

class GapPredictions(Base, TimestampMixin):
    """
    갭 예측 결과 테이블

    AI 서버에서 예측한 결과를 저장
    PredictionResultMessage 스키마 기반
    """

    __tablename__ = "predictions"

    # Primary Key - Auto Increment
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # =====================================================
    # 원본 정보
    # =====================================================
    # 예측 시각
    timestamp: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # 종목 코드
    stock_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # 종목명
    stock_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # 거래소 (KOSPI/KOSDAQ)
    exchange: Mapped[Exchange] = mapped_column(
        Enum(Exchange, create_type=False),
        nullable=True,
    )

    is_nxt: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
    )

    # 예측 대상 날짜
    prediction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # 전략 정보 (어떤 전략으로 예측했는지)
    strategy_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("strategy_info.id"),
        nullable=True,
    )

    # Relationship: N:1 (GapPredictions : StrategyInfo)
    strategy_info: Mapped[Optional["StrategyInfo"]] = relationship(
        "StrategyInfo",
        back_populates="gap_predictions",
    )

    # =====================================================
    # 입력 데이터
    # =====================================================
    # 갭 상승률 (%)
    gap_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # 당일 시가
    stock_open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # 예측 결과
    # =====================================================
    # 상승 확률 (0~1)
    prob_up: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # 하락 확률 (0~1)
    prob_down: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # 예측 방향 (0:하락, 1:상승)
    predicted_direction: Mapped[int] = mapped_column(
        nullable=False,
    )

    # 기대 수익률 (%)
    expected_return: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # 상승 시 예상 수익률 (%)
    return_if_up: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # 하락 시 예상 손실률 (%)
    return_if_down: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # 고가 예측 (선택)
    # =====================================================
    # 상승 시 최대 수익률 (%)
    max_return_if_up: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 익절 목표 수익률 (%)
    take_profit_target: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # =====================================================
    # 매매 신호
    # =====================================================
    # 매매 신호 (BUY/HOLD/SELL)
    signal: Mapped[SignalType] = mapped_column(
        Enum(SignalType),
        nullable=False,
        default=SignalType.HOLD,
    )

    # =====================================================
    # 메타 정보
    # =====================================================
    # 모델 버전
    model_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='v1.0',
    )

    # 신뢰도 (HIGH/MEDIUM/LOW)
    confidence: Mapped[Optional[ConfidenceLevel]] = mapped_column(
        Enum(ConfidenceLevel),
        nullable=True,
    )

    # =====================================================
    # 실제 결과 (Airflow에서 장 마감 후 업데이트)
    # =====================================================
    # 실제 종가
    actual_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 실제 고가
    actual_high: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 실제 저가
    actual_low: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # =====================================================
    # 예측 vs 실제 비교 (Airflow에서 계산하여 업데이트)
    # =====================================================
    # 실제 종가 수익률 (%) = (actual_close - stock_open) / stock_open * 100
    actual_return: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 종가 예측 차이 = expected_return - actual_return
    return_diff: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 실제 고가 수익률 (%) = (actual_high - stock_open) / stock_open * 100
    actual_max_return: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 고가 예측 차이 = max_return_if_up - actual_max_return
    max_return_diff: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 예측 방향 정확도 (1: 맞음, 0: 틀림)
    direction_correct: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # 제약 조건 및 인덱스
    # =====================================================
    __table_args__ = (
        # Unique: 종목 + 날짜 조합은 유일 (같은 날 같은 종목 중복 예측 방지)
        UniqueConstraint('stock_code', 'prediction_date', name='uq_gap_predictions_stock_date'),

        # Index: 조회 성능 최적화
        Index('idx_gap_predictions_stock_code', 'stock_code'),
        Index('idx_gap_predictions_date', 'prediction_date'),
        Index('idx_gap_predictions_signal', 'signal'),
    )

    def __repr__(self) -> str:
        return f"<GapPredictions(stock_code='{self.stock_code}', date={self.prediction_date}, signal={self.signal})>"

class UserStrategy(Base, TimestampMixin):
    __tablename__ = "user_strategy"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stock_accounts.id", ondelete="CASCADE"),
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

    account: Mapped["Accounts"] = relationship(
        "Accounts",
        back_populates="user_strategies",
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
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

    target_sell_price: Mapped[Optional[float]] = mapped_column(
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

class HourCandleData(Base, TimestampMixin):
    """1시간봉 캔들 데이터"""

    __tablename__ = "hour_candle_data"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 종목 코드
    stock_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # 캔들 날짜
    candle_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # 캔들 시간 (9, 10, 11, 12, 13, 14, 15)
    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # OHLCV 데이터
    open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    high: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    low: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    close: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    # 체결 건수
    trade_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        # Unique: 종목 + 날짜 + 시간 조합은 유일
        UniqueConstraint('stock_code', 'candle_date', 'hour', name='uq_hour_candle_stock_date_hour'),
        # Index: 조회 성능 최적화
        Index('idx_hour_candle_stock_code', 'stock_code'),
        Index('idx_hour_candle_date', 'candle_date'),
        Index('idx_hour_candle_stock_date', 'stock_code', 'candle_date'),
    )

    def __repr__(self) -> str:
        return f"<HourCandleData(stock_code='{self.stock_code}', date={self.candle_date}, hour={self.hour})>"


class MinuteCandleData(Base, TimestampMixin):
    """분봉 캔들 데이터 (1분, 3분, 5분, 10분, 15분, 30분 등)"""

    __tablename__ = "minute_candle_data"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 종목 코드
    stock_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # 캔들 날짜
    candle_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # 캔들 시간 (HH:MM:SS 형태로 저장, 예: 09:01:00, 09:05:00)
    candle_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    # 분봉 간격 (1, 3, 5, 10, 15, 30 등)
    minute_interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # OHLCV 데이터
    open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    high: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    low: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    close: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    # 체결 건수
    trade_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        # Unique: 종목 + 날짜 + 시간 + 분봉간격 조합은 유일
        UniqueConstraint(
            'stock_code', 'candle_date', 'candle_time', 'minute_interval',
            name='uq_minute_candle_stock_date_time_interval'
        ),
        # Index: 조회 성능 최적화
        Index('idx_minute_candle_stock_code', 'stock_code'),
        Index('idx_minute_candle_date', 'candle_date'),
        Index('idx_minute_candle_interval', 'minute_interval'),
        Index('idx_minute_candle_stock_date', 'stock_code', 'candle_date'),
        Index('idx_minute_candle_stock_date_interval', 'stock_code', 'candle_date', 'minute_interval'),
    )

    def __repr__(self) -> str:
        return f"<MinuteCandleData(stock_code='{self.stock_code}', date={self.candle_date}, time={self.candle_time}, interval={self.minute_interval}m)>"