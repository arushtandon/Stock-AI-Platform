"""
Stock selection engine: filter by liquidity/market cap and select Top N.
"""
from typing import List

from core.schemas import CompositeScore
from config import TOP_N_RECOMMENDATIONS, MIN_MARKET_CAP, MIN_AVG_VOLUME


# Placeholder: in production load from market data API
def get_market_cap(symbol: str) -> float:
    return 5e9  # default 5B for demo


def get_avg_volume(symbol: str) -> int:
    return 2_000_000  # default for demo


def filter_and_rank(
    composite_scores: List[CompositeScore],
    min_market_cap: float = MIN_MARKET_CAP,
    min_avg_volume: int = MIN_AVG_VOLUME,
    top_n: int = TOP_N_RECOMMENDATIONS,
) -> List[CompositeScore]:
    """Filter out low liquidity / small cap and return top N by composite score."""
    filtered = []
    for c in composite_scores:
        if get_market_cap(c.symbol) >= min_market_cap and get_avg_volume(c.symbol) >= min_avg_volume:
            filtered.append(c)
    filtered.sort(key=lambda x: x.composite_score, reverse=True)
    return filtered[:top_n]
