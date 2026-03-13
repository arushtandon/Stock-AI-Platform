"""App configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Database (default SQLite for dev; set DATABASE_URL for PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_ai.db")
# Redis: REDIS_URL or REDIS_HOST+REDIS_PORT (e.g. Render Key Value)
_redis_host = os.getenv("REDIS_HOST", "localhost")
_redis_port = os.getenv("REDIS_PORT", "6379")
REDIS_URL = os.getenv("REDIS_URL") or f"redis://{_redis_host}:{_redis_port}/0"

# Scoring weights (composite = 0.35 fund + 0.35 tech + 0.20 analyst + 0.10 sentiment)
WEIGHT_FUNDAMENTAL = float(os.getenv("WEIGHT_FUNDAMENTAL", "0.35"))
WEIGHT_TECHNICAL = float(os.getenv("WEIGHT_TECHNICAL", "0.35"))
WEIGHT_ANALYST = float(os.getenv("WEIGHT_ANALYST", "0.20"))
WEIGHT_SENTIMENT = float(os.getenv("WEIGHT_SENTIMENT", "0.10"))

# Filters
MIN_MARKET_CAP = float(os.getenv("MIN_MARKET_CAP", "1e9"))  # 1B
MIN_AVG_VOLUME = int(os.getenv("MIN_AVG_VOLUME", "500000"))
TOP_N_RECOMMENDATIONS = int(os.getenv("TOP_N_RECOMMENDATIONS", "20"))

# ATR multipliers by holding period
ATR_STOP_MULTIPLIER = float(os.getenv("ATR_STOP_MULTIPLIER", "2.0"))
ATR_TAKE_PROFIT_MULTIPLIER = float(os.getenv("ATR_TAKE_PROFIT_MULTIPLIER", "4.0"))
