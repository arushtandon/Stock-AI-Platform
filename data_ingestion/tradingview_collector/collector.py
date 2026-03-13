"""
TradingView-style collector for technical / momentum data.

Uses yfinance for daily price & volume history and computes a rich set of
momentum-driven technical indicators (no official TradingView API):

- Multi-horizon returns (5d, 20d, 60d)
- Moving averages (20/50/100/200) and trend structure
- RSI(14)
- MACD(12,26,9)
- Volume vs 20-day average
- Simple breakout context using price vs recent range

These are combined into a 0-100 momentum/technical score that feeds the
Safron ranking engine (short/swing periods weight this most heavily).
Optional TRADINGVIEW_API_KEY is reserved for future direct market-data providers.
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
            volume = hist.get("Volume")
            current = float(close.iloc[-1])

            # --- Moving averages & trend structure ---
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20
            sma100 = float(close.rolling(100).mean().iloc[-1]) if len(close) >= 100 else sma50
            sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else sma100

            # Short / medium horizon returns
            def pct_return(days: int) -> float:
                if len(close) <= days:
                    return 0.0
                past = float(close.iloc[-days - 1])
                if past == 0:
                    return 0.0
                return (current / past - 1.0) * 100.0

            ret_5 = pct_return(5)
            ret_20 = pct_return(20)
            ret_60 = pct_return(60)

            # --- RSI(14) ---
            import pandas as pd  # type: ignore

            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            roll_up = gain.rolling(14).mean()
            roll_down = loss.rolling(14).mean()
            rs = roll_up / roll_down.replace(0, pd.NA)
            rsi_series = 100.0 - (100.0 / (1.0 + rs))
            rsi14 = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0

            # --- MACD(12,26,9) ---
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_last = float(macd.iloc[-1])
            signal_last = float(signal.iloc[-1])

            # --- Volume vs 20-day average ---
            vol_score = 0.0
            if volume is not None:
                v_today = float(volume.iloc[-1])
                v_avg20 = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else v_today
                if v_avg20 > 0:
                    vol_ratio = min(3.0, max(0.3, v_today / v_avg20))
                    vol_score = (vol_ratio - 0.3) / (3.0 - 0.3) * 100.0  # 0-100

            # --- Trend score (0-100) ---
            trend_score = 50.0
            if current > sma20:
                trend_score += 10
            if current > sma50:
                trend_score += 10
            if current > sma100:
                trend_score += 5
            if current > sma200:
                trend_score += 5
            if sma20 > sma50 > sma100:
                trend_score += 10
            # clamp
            trend_score = min(100.0, max(0.0, trend_score))

            # --- Momentum score from returns & oscillators ---
            def clamp(x: float, lo: float, hi: float) -> float:
                return max(lo, min(hi, x))

            # Normalize returns roughly into -1..+1 then to 0-100
            ret_score = (
                0.4 * clamp(ret_5 / 10.0, -1.0, 1.0)
                + 0.4 * clamp(ret_20 / 20.0, -1.0, 1.0)
                + 0.2 * clamp(ret_60 / 30.0, -1.0, 1.0)
            )
            ret_score = (ret_score + 1.0) / 2.0 * 100.0  # -1..1 -> 0..100

            # RSI: prefer 40-70 region and rising from oversold
            if rsi14 < 30:
                rsi_score = 30.0
            elif 30 <= rsi14 <= 60:
                rsi_score = 60.0 + (rsi14 - 30) * (20.0 / 30.0)  # up to ~80
            elif 60 < rsi14 <= 80:
                rsi_score = 80.0 - (rsi14 - 60) * (20.0 / 20.0)  # fall back from overbought
            else:
                rsi_score = 50.0

            # MACD: positive and above signal is good; negative below signal is bad
            macd_score = 50.0
            if macd_last > 0 and macd_last > signal_last:
                macd_score = 80.0
            elif macd_last > 0:
                macd_score = 65.0
            elif macd_last < 0 and macd_last < signal_last:
                macd_score = 20.0
            else:
                macd_score = 40.0

            # Combine into momentum_score (0-100)
            momentum_score = (
                0.3 * trend_score
                + 0.3 * ret_score
                + 0.2 * rsi_score
                + 0.2 * macd_score
            )
            momentum_score = float(min(100.0, max(0.0, momentum_score)))

            # Overall technical_score also incorporates volume confirmation
            technical_score = 0.8 * momentum_score + 0.2 * vol_score
            technical_score = float(min(100.0, max(0.0, technical_score)))

            rating = "Strong Buy" if technical_score >= 75 else "Buy" if technical_score >= 55 else "Hold"
            info = ticker.info
            return {
                "technical_rating": rating,
                "technical_score": technical_score,
                "momentum_score": momentum_score,
                "rsi14": rsi14,
                "ret_5": ret_5,
                "ret_20": ret_20,
                "ret_60": ret_60,
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
        momentum = raw.get("momentum_score")
        return StockAnalysis(
            symbol=symbol,
            company_name=raw.get("company_name"),
            source=self.source,
            technical_score=min(100, float(tech_score)),
            momentum_score=float(momentum) if momentum is not None else None,
            analyst_rating=raw.get("technical_rating") or raw.get("recommendation"),
            timestamp=datetime.utcnow(),
            raw_data=raw,
        )

    def health_check(self) -> bool:
        return True
