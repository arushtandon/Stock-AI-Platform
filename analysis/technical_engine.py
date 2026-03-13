"""
Technical analysis engine: aggregates technical scores from all sources.
"""
from collections import defaultdict
from typing import List

from core.schemas import StockAnalysis


def aggregate_technical_by_symbol(analyses: List[StockAnalysis]) -> dict[str, float]:
    """For each symbol, compute average technical score (0-100)."""
    by_symbol: dict[str, List[float]] = defaultdict(list)
    for a in analyses:
        if a.technical_score is not None:
            by_symbol[a.symbol].append(a.technical_score)
        if a.momentum_score is not None:
            by_symbol[a.symbol].append(a.momentum_score)
    return {
        sym: sum(scores) / len(scores) if scores else 50.0
        for sym, scores in by_symbol.items()
    }
