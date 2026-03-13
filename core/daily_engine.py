"""
Daily recommendation engine: refresh data, rank, select Top 20, compute entry/stop/targets.
Runs before market open; publishes to DB and triggers alerts.
"""
import logging
from datetime import datetime
from typing import List

from core.schemas import StockAnalysis, CompositeScore, StockRecommendation, HoldingPeriod
from core.universe import get_universe_symbols
from data_ingestion.pipeline import run_ingestion
from analysis.ranking_engine import build_composite_scores
from analysis.selection_engine import filter_and_rank
from risk.stoploss_engine import (
    compute_levels,
    risk_reward_ratio,
    expected_return_pct,
    position_risk_pct,
)
from risk.volatility_engine import get_atr, get_support_resistance

logger = logging.getLogger(__name__)
DEFAULT_HOLDING_PERIOD = HoldingPeriod.MEDIUM_TERM


def _entry_price(symbol: str) -> float:
    """Placeholder: use last close from market data. In production, use real API."""
    # Demo: deterministic from symbol
    base = 100 + (hash(symbol) % 900)
    return float(base)


def generate_daily_recommendations(
    symbols: List[str] | None = None,
    holding_period: HoldingPeriod = DEFAULT_HOLDING_PERIOD,
    top_n: int = 20,
) -> List[StockRecommendation]:
    """
    1. Run ingestion from all sources
    2. Build composite scores
    3. Filter and select top N
    4. For each: entry, stop, take profit, risk/reward, sources
    """
    symbols = symbols or get_universe_symbols(limit=500)
    analyses: List[StockAnalysis] = run_ingestion(symbols=symbols)
    if not analyses:
        logger.warning("No analyses collected")
        return []

    composite_scores = build_composite_scores(analyses)
    top = filter_and_rank(composite_scores, top_n=top_n)

    # Build source list per symbol from analyses
    sources_by_symbol: dict[str, set[str]] = {}
    for a in analyses:
        sources_by_symbol.setdefault(a.symbol, set()).add(a.source.value)
    company_by_symbol = {a.symbol: a.company_name for a in analyses if a.company_name}

    recommendations = []
    for c in top:
        entry = _entry_price(c.symbol)
        atr = get_atr(c.symbol)
        stop_loss, take_profit = compute_levels(entry, atr, holding_period)
        support, resistance = get_support_resistance(c.symbol, entry)
        rr = risk_reward_ratio(entry, stop_loss, take_profit)
        rec = StockRecommendation(
            symbol=c.symbol,
            company_name=company_by_symbol.get(c.symbol),
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=rr,
            composite_score=c.composite_score,
            holding_period=holding_period,
            sources=sorted(sources_by_symbol.get(c.symbol, [])),
            expected_return_pct=expected_return_pct(entry, take_profit),
            position_risk_pct=position_risk_pct(entry, stop_loss),
            support_level=support,
            resistance_level=resistance,
            atr=atr,
            timestamp=datetime.utcnow(),
        )
        recommendations.append(rec)
    return recommendations
