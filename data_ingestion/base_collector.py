"""
Base collector interface for all platform data sources.
"""
from abc import ABC, abstractmethod
from typing import List

from core.schemas import StockAnalysis, DataSource


class BaseCollector(ABC):
    """Abstract base for platform-specific collectors."""

    source: DataSource

    @abstractmethod
    def collect(self, symbols: List[str]) -> List[StockAnalysis]:
        """Fetch and normalize analysis for given symbols. Returns unified StockAnalysis list."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify connection/credentials to the platform."""
        pass
