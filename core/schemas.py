"""
Unified schemas for stock analysis across all data sources.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HoldingPeriod(str, Enum):
    SHORT_TERM = "short_term"      # 1-7 days
    SWING = "swing"               # 1-4 weeks
    MEDIUM_TERM = "medium_term"   # 1-3 months
    LONG_TERM = "long_term"       # 6-12 months


class DataSource(str, Enum):
    DANELFIN = "danelfin"
    SEEKING_ALPHA = "seeking_alpha"
    INVESTING_PRO = "investing_pro"
    TRADINGVIEW = "tradingview"


class StockAnalysis(BaseModel):
    """Unified stock analysis record from any source."""
    symbol: str
    company_name: Optional[str] = None
    source: DataSource
    fundamental_score: Optional[float] = None  # 0-100
    technical_score: Optional[float] = None     # 0-100
    sentiment_score: Optional[float] = None    # 0-100
    analyst_rating: Optional[str] = None       # e.g. "Strong Buy", "Buy"
    ai_rating: Optional[float] = None          # 0-100
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Extended fields for normalization
    financial_health_score: Optional[float] = None
    momentum_score: Optional[float] = None
    earnings_growth: Optional[float] = None
    revenue_growth: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    raw_data: Optional[dict] = None


class CompositeScore(BaseModel):
    """Aggregated composite score for a stock."""
    symbol: str
    composite_score: float  # 0-100
    fundamental_component: float
    technical_component: float
    analyst_component: float
    sentiment_component: float
    source_breakdown: dict  # per-source contributions
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StockRecommendation(BaseModel):
    """Daily top pick with entry, stop, targets."""
    symbol: str
    company_name: Optional[str] = None
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: str  # e.g. "1:3"
    composite_score: float
    holding_period: HoldingPeriod
    sources: list[str]
    expected_return_pct: Optional[float] = None
    position_risk_pct: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    atr: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskMetrics(BaseModel):
    """Risk metrics for a recommendation."""
    symbol: str
    volatility_annual: Optional[float] = None
    max_drawdown_probability: Optional[float] = None
    beta_vs_index: Optional[float] = None
    atr: Optional[float] = None
    support: Optional[float] = None
    resistance: Optional[float] = None
    stop_loss_atr_multiplier: float = 2.0
    take_profit_atr_multiplier: float = 4.0
