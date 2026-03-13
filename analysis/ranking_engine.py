"""
Multi-source ranking engine.
Composite Score = 0.35*Fundamental + 0.35*Technical + 0.20*Analyst + 0.10*Sentiment
All scores normalized 0-100.
"""
from collections import defaultdict
from typing import List

from core.schemas import StockAnalysis, CompositeScore, DataSource
from analysis.fundamental_engine import aggregate_fundamental_by_symbol
from analysis.technical_engine import aggregate_technical_by_symbol
from config import (
    WEIGHT_FUNDAMENTAL,
    WEIGHT_TECHNICAL,
    WEIGHT_ANALYST,
    WEIGHT_SENTIMENT,
)


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


def build_composite_scores(analyses: List[StockAnalysis]) -> List[CompositeScore]:
    """Build composite scores for all symbols present in analyses."""
    from datetime import datetime

    fund = aggregate_fundamental_by_symbol(analyses)
    tech = aggregate_technical_by_symbol(analyses)
    analyst = _aggregate_analyst_by_symbol(analyses)
    sentiment = _aggregate_sentiment_by_symbol(analyses)

    symbols = set(fund.keys()) | set(tech.keys()) | set(analyst.keys()) | set(sentiment.keys())
    source_breakdown = _source_breakdown(analyses)

    result = []
    for sym in symbols:
        f = fund.get(sym, 50.0)
        t = tech.get(sym, 50.0)
        a = analyst.get(sym, 50.0)
        s = sentiment.get(sym, 50.0)
        composite = (
            WEIGHT_FUNDAMENTAL * f
            + WEIGHT_TECHNICAL * t
            + WEIGHT_ANALYST * a
            + WEIGHT_SENTIMENT * s
        )
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
