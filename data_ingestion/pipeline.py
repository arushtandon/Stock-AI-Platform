"""
Data ingestion pipeline: run all collectors and persist to central DB.
"""
import logging
from datetime import datetime
from typing import List

from core.schemas import StockAnalysis, DataSource
from core.universe import get_universe_symbols
from data_ingestion.danelfin_collector import DanelfinCollector
from data_ingestion.seekingalpha_collector import SeekingAlphaCollector
from data_ingestion.investingpro_collector import InvestingProCollector
from data_ingestion.tradingview_collector import TradingViewCollector

logger = logging.getLogger(__name__)


def run_ingestion(symbols: List[str] | None = None, limit_per_source: int = 500) -> List[StockAnalysis]:
    """Run all collectors and return combined normalized analyses."""
    symbols = symbols or get_universe_symbols(limit=limit_per_source)
    collectors = [
        DanelfinCollector(),
        SeekingAlphaCollector(),
        InvestingProCollector(),
        TradingViewCollector(),
    ]
    all_analyses: List[StockAnalysis] = []
    for coll in collectors:
        try:
            batch = coll.collect(symbols)
            all_analyses.extend(batch)
            logger.info("Collected %d records from %s", len(batch), coll.source.value)
        except Exception as e:
            logger.exception("Collector %s failed: %s", coll.source.value, e)
    return all_analyses
