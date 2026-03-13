"""
Danelfin AI-powered stock analysis collector.
Normalizes AI score, fundamental and technical signals into unified schema.
"""
import os
from datetime import datetime
from typing import List

from core.schemas import StockAnalysis, DataSource
from data_ingestion.base_collector import BaseCollector


class DanelfinCollector(BaseCollector):
    source = DataSource.DANELFIN

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("DANELFIN_API_KEY", "")
        self.base_url = os.getenv("DANELFIN_BASE_URL", "https://api.danelfin.com/v1")

    def collect(self, symbols: List[str]) -> List[StockAnalysis]:
        """Fetch Danelfin AI scores and fundamentals. In production, call real API."""
        results = []
        # Placeholder: real implementation would use requests/httpx with API key
        for symbol in symbols:
            # Simulated response structure - replace with actual API call
            raw = self._fetch_symbol(symbol)
            if raw:
                results.append(self._normalize(symbol, raw))
        return results

    def _fetch_symbol(self, symbol: str) -> dict | None:
        """Call Danelfin API. Returns raw dict or None on failure."""
        if not self.api_key:
            # Demo mode: return synthetic data
            return {
                "ai_score": 75 + hash(symbol) % 25,
                "fundamental_score": 70 + hash(symbol) % 25,
                "technical_score": 65 + (hash(symbol) >> 4) % 25,
                "sentiment": 60 + (hash(symbol) >> 8) % 30,
                "company_name": f"{symbol} Inc.",
            }
        # TODO: requests.get(f"{self.base_url}/stocks/{symbol}", headers={"Authorization": f"Bearer {self.api_key}"})
        return None

    def _normalize(self, symbol: str, raw: dict) -> StockAnalysis:
        return StockAnalysis(
            symbol=symbol,
            company_name=raw.get("company_name"),
            source=self.source,
            fundamental_score=float(raw.get("fundamental_score", 0)),
            technical_score=float(raw.get("technical_score", 0)),
            sentiment_score=float(raw.get("sentiment", 0)),
            ai_rating=float(raw.get("ai_score", 0)),
            timestamp=datetime.utcnow(),
            raw_data=raw,
        )

    def health_check(self) -> bool:
        if not self.api_key:
            return True  # Demo mode
        # TODO: GET /health or similar
        return True
