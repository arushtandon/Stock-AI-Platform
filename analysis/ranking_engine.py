"""
Multi-source Safron ranking engine.
Base composite model:
  Composite = w_fund * Fundamental + w_tech * Technical + w_analyst * Analyst + w_sentiment * Sentiment
Weights are adjusted by holding period so that short-term ideas lean more on technicals/momentum
and long-term ideas lean more on fundamentals.
All scores are normalized to 0-100.
"""
from collections import defaultdict
from typing import List

from core.schemas import StockAnalysis, CompositeScore, DataSource, HoldingPeriod
from analysis.fundamental_engine import aggregate_fundamental_by_symbol
from analysis.technical_engine import aggregate_technical_by_symbol
from config import WEIGHT_FUNDAMENTAL, WEIGHT_TECHNICAL, WEIGHT_ANALYST, WEIGHT_SENTIMENT


# Map analyst rating text to 0-100
ANALYST_MAP = {
    "strong buy": 95,
    "buy": 75,
    "hold": 50,
    "sell": 25,
    "strong sell": 5,
}


def _analyst_to_score(rating: str | None) -> float:
    if not rating:
        return 50.0
    key = rating.lower().strip()
    return ANALYST_MAP.get(key, 50.0)


def _aggregate_analyst_by_symbol(analyses: List[StockAnalysis]) -> dict[str, float]:
    by_symbol: dict[str, List[float]] = defaultdict(list)
    for a in analyses:
        s = _analyst_to_score(a.analyst_rating)
        by_symbol[a.symbol].append(s)
        if a.ai_rating is not None:
            by_symbol[a.symbol].append(a.ai_rating)
    return {
        sym: sum(scores) / len(scores) if scores else 50.0
        for sym, scores in by_symbol.items()
    }


def _aggregate_sentiment_by_symbol(analyses: List[StockAnalysis]) -> dict[str, float]:
    by_symbol: dict[str, List[float]] = defaultdict(list)
    for a in analyses:
        if a.sentiment_score is not None:
            by_symbol[a.symbol].append(a.sentiment_score)
    return {
        sym: sum(scores) / len(scores) if scores else 50.0
        for sym, scores in by_symbol.items()
    }


def _weights_for_period(holding_period: HoldingPeriod | None) -> tuple[float, float, float, float]:
    """
    Return (w_fund, w_tech, w_analyst, w_sentiment) for a given holding period.

    - Short term / swing: emphasize technicals & sentiment
    - Medium term: balanced (use config defaults)
    - Long term: emphasize fundamentals & analyst view
    """
    if holding_period in (HoldingPeriod.SHORT_TERM, HoldingPeriod.SWING):
        return (0.2, 0.55, 0.15, 0.10)
    if holding_period == HoldingPeriod.LONG_TERM:
        return (0.5, 0.25, 0.15, 0.10)
    # medium term or None: use configured defaults
    return (WEIGHT_FUNDAMENTAL, WEIGHT_TECHNICAL, WEIGHT_ANALYST, WEIGHT_SENTIMENT)


def build_composite_scores(
    analyses: List[StockAnalysis],
    holding_period: HoldingPeriod | None = None,
) -> List[CompositeScore]:
    """Build Safron composite scores for all symbols present in analyses."""
    from datetime import datetime

    fund = aggregate_fundamental_by_symbol(analyses)
    tech = aggregate_technical_by_symbol(analyses)
    analyst = _aggregate_analyst_by_symbol(analyses)
    sentiment = _aggregate_sentiment_by_symbol(analyses)

    symbols = set(fund.keys()) | set(tech.keys()) | set(analyst.keys()) | set(sentiment.keys())
    source_breakdown = _source_breakdown(analyses)

    w_fund, w_tech, w_analyst, w_sentiment = _weights_for_period(holding_period)

    result = []
    for sym in symbols:
        f = fund.get(sym, 50.0)
        t = tech.get(sym, 50.0)
        a = analyst.get(sym, 50.0)
        s = sentiment.get(sym, 50.0)
        composite = w_fund * f + w_tech * t + w_analyst * a + w_sentiment * s
        result.append(
            CompositeScore(
                symbol=sym,
                composite_score=round(min(100, max(0, composite)), 2),
                fundamental_component=round(f, 2),
                technical_component=round(t, 2),
                analyst_component=round(a, 2),
                sentiment_component=round(s, 2),
                source_breakdown=source_breakdown.get(sym, {}),
                timestamp=datetime.utcnow(),
            )
        )
    return result


def _source_breakdown(analyses: List[StockAnalysis]) -> dict[str, dict]:
    """Per-symbol breakdown of which sources contributed."""
    by_symbol: dict[str, dict[str, float]] = defaultdict(dict)
    for a in analyses:
        score = 50.0
        if a.fundamental_score is not None:
            score = (score + a.fundamental_score) / 2
        if a.technical_score is not None:
            score = (score + a.technical_score) / 2
        if a.ai_rating is not None:
            score = (score + a.ai_rating) / 2
        by_symbol[a.symbol][a.source.value] = round(score, 2)
    return dict(by_symbol)
