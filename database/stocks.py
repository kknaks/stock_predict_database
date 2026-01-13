"""
Stock Data 모델

주식 가격 데이터 및 기술적 지표
- StockMetadata: 종목 메타 정보
- StockPrices: 일별 OHLCV + 기술지표 (미리 계산)
- MarketIndices: 시장 지수 (KOSPI/KOSDAQ)
"""

import enum
from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, Enum, Float, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Exchange(str, enum.Enum):
    """거래소"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"


class StockStatus(str, enum.Enum):
    """종목 상태"""
    ACTIVE = "ACTIVE"           # 정상 거래
    DELISTED = "DELISTED"       # 상장폐지
    SUSPENDED = "SUSPENDED"     # 거래정지
    WARNING = "WARNING"         # 관리종목


class StockMetadata(Base, TimestampMixin):
    """종목 메타 정보 테이블"""

    __tablename__ = "stock_metadata"

    # Primary Key - 종목 코드
    symbol: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    # 종목 기본 정보
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    exchange: Mapped[Exchange] = mapped_column(
        Enum(Exchange),
        nullable=False,
    )

    sector: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # 시가총액 (원)
    market_cap: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )

    # 상장/상장폐지 정보
    listing_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[StockStatus] = mapped_column(
        Enum(StockStatus),
        nullable=False,
        default=StockStatus.ACTIVE,
    )

    delist_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # Relationship: 1:N (StockMetadata : StockPrices)
    prices: Mapped[list["StockPrices"]] = relationship(
        "StockPrices",
        back_populates="stock",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<StockMetadata(symbol='{self.symbol}', name='{self.name}')>"


class StockPrices(Base, TimestampMixin):
    """
    종목 일별 가격 + 기술지표 테이블

    모든 기술지표를 미리 계산해서 저장
    - AI 서버는 조회만 하면 됨 (계산 불필요)
    """

    __tablename__ = "stock_prices"

    # Primary Key - Auto Increment
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 종목 코드 + 날짜 (Unique)
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stock_metadata.symbol", ondelete="CASCADE"),
        nullable=False,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Relationship: N:1 (StockPrices : StockMetadata)
    stock: Mapped["StockMetadata"] = relationship(
        "StockMetadata",
        back_populates="prices",
    )

    # =====================================================
    # OHLCV (원본 데이터)
    # =====================================================
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
    )

    # =====================================================
    # 가격 기반 Features (미리 계산)
    # =====================================================

    # 전일 종가 (gap 계산용)
    prev_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 갭 비율 (%)
    gap_pct: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 전일 수익률 (%)
    prev_return: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 전일 고저가 범위 (%)
    prev_range_pct: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 전일 윗꼬리
    prev_upper_shadow: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 전일 아래꼬리
    prev_lower_shadow: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 거래량 비율 (전일 / 20일 평균)
    volume_ratio: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # 기술적 지표 Features (미리 계산)
    # =====================================================

    # RSI 14일
    rsi_14: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # ATR 14일
    atr_14: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # ATR 비율 (갭 크기 / ATR)
    atr_ratio: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 볼린저밴드 위치 (0~1)
    bollinger_position: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 볼린저밴드 (참고용)
    bollinger_upper: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    bollinger_middle: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    bollinger_lower: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 이동평균선
    ma_5: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    ma_20: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    ma_50: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # 이동평균선 위/아래 (0 or 1)
    above_ma5: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    above_ma20: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    above_ma50: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 골든크로스/데드크로스 (0 or 1)
    ma5_ma20_cross: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 수익률 (%)
    return_5d: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    return_20d: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # 연속 상승일
    consecutive_up_days: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # 시장 컨텍스트 Features (미리 계산)
    # =====================================================

    # 시장 대비 갭 차이 (종목 갭 - KOSPI/KOSDAQ 갭) ⭐ Feature Importance 1위!
    market_gap_diff: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # 제약 조건 및 인덱스
    # =====================================================
    __table_args__ = (
        # Unique: 종목 + 날짜 조합은 유일
        UniqueConstraint('symbol', 'date', name='uq_stock_prices_symbol_date'),

        # Index: 조회 성능 최적화
        Index('idx_stock_prices_symbol_date', 'symbol', 'date'),
        Index('idx_stock_prices_date', 'date'),
    )

    def __repr__(self) -> str:
        return f"<StockPrices(symbol='{self.symbol}', date={self.date})>"


class MarketIndices(Base, TimestampMixin):
    """
    시장 지수 테이블 (KOSPI/KOSDAQ)

    갭 계산을 미리 해서 저장
    """

    __tablename__ = "market_indices"

    # Primary Key - 날짜
    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )

    # =====================================================
    # KOSPI
    # =====================================================
    kospi_open: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi_high: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi_low: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi_volume: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # KOSPI 갭 (%) - 미리 계산
    kospi_gap_pct: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # KOSDAQ
    # =====================================================
    kosdaq_open: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kosdaq_high: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kosdaq_low: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kosdaq_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kosdaq_volume: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # KOSDAQ 갭 (%) - 미리 계산
    kosdaq_gap_pct: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # KOSPI200 (선택)
    # =====================================================
    kospi200_open: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi200_high: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi200_low: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi200_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    kospi200_volume: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    kospi200_gap_pct: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # 인덱스
    # =====================================================
    __table_args__ = (
        Index('idx_market_indices_date', 'date'),
    )

    def __repr__(self) -> str:
        return f"<MarketIndices(date={self.date})>"

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


class GapPredictions(Base, TimestampMixin):
    """
    갭 예측 결과 테이블

    AI 서버에서 예측한 결과를 저장
    PredictionResultMessage 스키마 기반
    """

    __tablename__ = "gap_predictions"

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

    # # 거래소 (KOSPI/KOSDAQ)
    # exchange: Mapped[Exchange] = mapped_column(
    #     Enum(Exchange),
    #     nullable=False,
    # )

    # 예측 대상 날짜
    prediction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
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