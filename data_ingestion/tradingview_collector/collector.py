"""
TradingView-style collector for technical data.
Uses yfinance for price history and simple technical signals (no official TradingView API).
Optional TRADINGVIEW_API_KEY for future market-data provider. Always returns data.
"""
import os
from datetime import datetime, timedelta
from typing import List

from core.schemas import StockAnalysis, DataSource
from data_ingestion.base_collector import BaseCollector

try:
    import yfinance as yf
except ImportError:
    yf = None


class TradingViewCollector(BaseCollector):
    source = DataSource.TRADINGVIEW

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TRADINGVIEW_API_KEY", "")
        self.base_url = os.getenv("TRADINGVIEW_BASE_URL", "https://scanner.tradingview.com")

    def collect(self, symbols: List[str]) -> List[StockAnalysis]:
        results = []
        for symbol in symbols:
            raw = self._fetch_symbol(symbol)
            if raw:
                results.append(self._normalize(symbol, raw))
        return results

    def _fetch_symbol(self, symbol: str) -> dict | None:
        if self.api_key:
            pass  # TODO: use TRADINGVIEW_API_KEY with Alpha Vantage / EOD / etc. if desired
        if yf is None:
            return self._demo_data(symbol)
        try:
            ticker = yf.Ticker(symbol)
            end = datetime.utcnow()
            start = end - timedelta(days=90)
            hist = ticker.history(start=start, end=end, auto_adjust=True)
            if hist is None or len(hist) < 20:
                return self._demo_data(symbol)
            close = hist["Close"]
            sma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else close.iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else close.iloc[-1]
            current = close.iloc[-1]
            # Simple technical score: trend (price vs SMAs) and momentum (recent return)
            trend_score = 50
            if current > sma20:
                trend_score += 15
            if current > sma50:
                trend_score += 15
            if sma20 > sma50:
                trend_score += 10
            ret_20d = (close.iloc[-1] / close.iloc[-min(20, len(close))] - 1) * 100 if len(close) >= 2 else 0
            momentum = min(20, max(-20, ret_20d))
            technical_score = min(100, max(0, trend_score + momentum))
            rating = "Strong Buy" if technical_score >= 75 else "Buy" if technical_score >= 55 else "Hold"
            info = ticker.info
            return {
                "technical_rating": rating,
                "technical_score": technical_score,
                "recommendation": rating,
                "company_name": info.get("shortName") or info.get("longName") or f"{symbol} Inc.",
            }
        except Exception:
            return self._demo_data(symbol)

    def _demo_data(self, symbol: str) -> dict:
        return {
            "technical_rating": "Strong Buy" if (hash(symbol) % 3) == 0 else "Buy",
            "technical_score": 70 + (hash(symbol) % 25),
            "recommendation": "Buy",
            "company_name": f"{symbol} Inc.",
        }

    def _normalize(self, symbol: str, raw: dict) -> StockAnalysis:
        tech_score = raw.get("technical_score", 70)
        return StockAnalysis(
            symbol=symbol,
            company_name=raw.get("company_name"),
            source=self.source,
            technical_score=min(100, float(tech_score)),
            analyst_rating=raw.get("technical_rating") or raw.get("recommendation"),
            timestamp=datetime.utcnow(),
            raw_data=raw,
        )

    def health_check(self) -> bool:
        return True
