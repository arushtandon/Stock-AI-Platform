"""
Volatility and risk metrics: ATR, support/resistance from price history.
Uses yfinance for OHLC; important for short- and mid-term recommendations.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from core.schemas import RiskMetrics

try:
    import yfinance as yf
except ImportError:
    yf = None


def _get_history(symbol: str, days: int = 90):
    """Return recent daily OHLCV for symbol."""
    if yf is None:
        return None
    try:
        t = yf.Ticker(symbol)
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        hist = t.history(start=start, end=end, auto_adjust=True)
        if hist is None or len(hist) < 14:
            return None
        return hist
    except Exception:
        return None


def get_atr(symbol: str, period: int = 14) -> float:
    """ATR(period) from price history. Fallback to ~2% of price if no data."""
    hist = _get_history(symbol, days=90)
    if hist is None or len(hist) < period + 1:
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            price = info.get("regularMarketPrice") or 100.0
            return float(price) * 0.02
        except Exception:
            return 2.0
    high = hist["High"]
    low = hist["Low"]
    close = hist["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr_val = tr.rolling(period).mean().iloc[-1]
    return float(atr_val) if atr_val and not math.isnan(atr_val) else 2.0


def get_support_resistance(symbol: str, current_price: float) -> tuple[Optional[float], Optional[float]]:
    """
    Support and resistance from recent swing lows/highs (last ~60 days).
    Uses rolling 5-day min for support candidates and 5-day max for resistance.
    """
    hist = _get_history(symbol, days=90)
    if hist is None or len(hist) < 20:
        support = round(current_price * 0.95, 2)
        resistance = round(current_price * 1.08, 2)
        return support, resistance
    close = hist["Close"]
    low = hist["Low"]
    high = hist["High"]
    # Recent swing lows (local minima) as support
    roll_low = low.rolling(5, center=True).min()
    recent_lows = roll_low.iloc[-30:].dropna()
    support_candidates = recent_lows[recent_lows <= current_price]
    support = float(support_candidates.iloc[-1]) if len(support_candidates) > 0 else float(low.iloc[-20:].min())
    # Recent swing highs as resistance
    roll_high = high.rolling(5, center=True).max()
    recent_highs = roll_high.iloc[-30:].dropna()
    resistance_candidates = recent_highs[recent_highs >= current_price]
    resistance = float(resistance_candidates.iloc[0]) if len(resistance_candidates) > 0 else float(high.iloc[-20:].max())
    # Sanity: support below current, resistance above
    if support >= current_price:
        support = float(low.iloc[-20:].min()) if len(low.iloc[-20:]) else current_price * 0.95
    if resistance <= current_price:
        resistance = float(high.iloc[-20:].max()) if len(high.iloc[-20:]) else current_price * 1.08
    return round(support, 2), round(resistance, 2)


def get_volatility_beta(symbol: str) -> tuple[Optional[float], Optional[float]]:
    """Placeholder: annual volatility and beta vs index."""
    return 0.25, 1.1


def build_risk_metrics(
    symbol: str,
    entry_price: float,
    atr: Optional[float] = None,
    stop_mult: float = 2.0,
    tp_mult: float = 4.0,
) -> RiskMetrics:
    atr = atr or get_atr(symbol)
    vol, beta = get_volatility_beta(symbol)
    support, resistance = get_support_resistance(symbol, entry_price)
    return RiskMetrics(
        symbol=symbol,
        volatility_annual=vol,
        beta_vs_index=beta,
        atr=atr,
        support=support,
        resistance=resistance,
        stop_loss_atr_multiplier=stop_mult,
        take_profit_atr_multiplier=tp_mult,
    )
