"""
Volatility and risk metrics: ATR, support/resistance, drawdown probability.
In production, compute from price history (e.g. yfinance or market data API).
"""
from typing import Optional

from core.schemas import RiskMetrics


def get_atr(symbol: str, period: int = 14) -> float:
    """Placeholder: return synthetic ATR. Replace with real price history."""
    # Demo: ~2% of a nominal price
    base = 100 if "BRK" not in symbol else 400
    return base * 0.02


def get_support_resistance(symbol: str, current_price: float) -> tuple[Optional[float], Optional[float]]:
    """Placeholder: return support and resistance levels."""
    support = current_price * 0.95
    resistance = current_price * 1.08
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
