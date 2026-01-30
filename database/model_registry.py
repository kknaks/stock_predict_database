"""
모델 레지스트리 테이블

모델 버전 관리, 학습 메타데이터, 테스트 메트릭, 상태 추적
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ModelStatus(str, enum.Enum):
    """모델 상태"""
    CANDIDATE = "candidate"  # 학습 완료, 비교 대기
    ACTIVE = "active"        # 현재 서빙 중
    RETIRED = "retired"      # 이전 모델 (비활성)
    REJECTED = "rejected"    # 비교에서 탈락


class ModelRegistry(Base, TimestampMixin):
    """모델 레지스트리 테이블"""

    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # 버전 정보
    version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    model_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # 학습 메타데이터
    training_data_start: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )

    training_data_end: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )

    training_samples: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    training_duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    trigger_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # 학습 하이퍼파라미터
    hyperparameters: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # 테스트 메트릭
    test_metrics: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Champion-Challenger 비교 결과
    comparison_result: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # 상태
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus),
        nullable=False,
        default=ModelStatus.CANDIDATE,
    )

    # 활성화 시각
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ModelRegistry(version='{self.version}', status={self.status})>"
