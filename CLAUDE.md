# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Predict Database is a PostgreSQL async database layer for a Korean stock prediction system. It provides SQLAlchemy 2.0 models with Alembic migrations, designed to work with AI prediction servers and trading automation via Korea Investment & Securities (KIS) API.

## Commands

### Development Setup
```bash
poetry install                    # Install dependencies
cp env.example .env              # Configure environment
docker compose up -d             # Start PostgreSQL + Redpanda (Kafka)
```

### Database Migrations
```bash
alembic upgrade head             # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1             # Rollback one migration
```

### Code Quality
```bash
poetry run black .               # Format code (line-length: 100)
poetry run flake8                # Lint
poetry run mypy .                # Type check (uses sqlalchemy.ext.mypy.plugin)
poetry run pytest                # Run tests (asyncio_mode=auto)
```

## Architecture

### Database Models (`database/`)

All models inherit from `Base` (DeclarativeBase) and use `TimestampMixin` for `created_at`/`updated_at` fields.

**Stock Data Domain:**
- `StockMetadata` - Stock metadata (symbol as PK, exchange KOSPI/KOSDAQ, status)
- `StockPrices` - Daily OHLCV with pre-computed technical indicators (RSI, ATR, Bollinger, MAs, etc.)
- `MarketIndices` - Market indices (KOSPI/KOSDAQ/KOSPI200) with gap percentages
- `GapPredictions` - AI prediction results with actual vs predicted comparison fields

**User/Trading Domain:**
- `Users` - User accounts with RBAC (master/user/mock roles)
- `Accounts` - KIS brokerage accounts with API credentials and token caching
- `StrategyInfo`, `StrategyWeightType`, `UserStrategy` - Trading strategy configuration
- `DailyStrategy`, `DailyStrategyStock` - Daily trading execution records
- `Order`, `OrderExecution` - Order tracking with execution history

### Key Design Patterns

1. **Pre-computed Features**: `StockPrices` stores pre-calculated technical indicators so AI servers only query (no computation needed)

2. **Prediction Tracking**: `GapPredictions` has both prediction fields (`prob_up`, `expected_return`) and actual result fields (`actual_close`, `direction_correct`) updated post-market

3. **Order State Machine**: `Order` tracks cumulative execution state; `OrderExecution` stores individual fill events

### Infrastructure

- **PostgreSQL 16** with async driver (asyncpg)
- **Redpanda** (Kafka-compatible) 3-node cluster for event streaming
- Topics: `extract_daily_candidate`, `kis_websocket_commands`

### Environment Variables

Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
Kafka: `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_GROUP_ID`
