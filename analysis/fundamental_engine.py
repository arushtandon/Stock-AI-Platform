"""
Fundamental analysis engine: aggregates fundamental scores from all sources.
"""
from collections import defaultdict
from typing import List

from core.schemas import StockAnalysis, DataSource


def aggregate_fundamental_by_symbol(analyses: List[StockAnalysis]) -> dict[str, float]:
    """For each symbol, compute average fundamental score (0-100) from all sources."""
    by_symbol: dict[str, List[float]] = defaultdict(list)
    for a in analyses:
        if a.fundamental_score is not None:
            by_symbol[a.symbol].append(a.fundamental_score)
        if a.financial_health_score is not None:
            by_symbol[a.symbol].append(a.financial_health_score)
    return {
        sym: sum(scores) / len(scores) if scores else 50.0
        for sym, scores in by_symbol.items()
    }
