"""
Stop loss and take profit engine.
Stop Loss = Entry - 2*ATR, Take Profit = Entry + 4*ATR (configurable).
"""
from core.schemas import HoldingPeriod, RiskMetrics
from config import ATR_STOP_MULTIPLIER, ATR_TAKE_PROFIT_MULTIPLIER


# ATR multipliers by holding period (tighter for short term)
ATR_MULTIPLIERS = {
    HoldingPeriod.SHORT_TERM: (1.5, 3.0),
    HoldingPeriod.SWING: (2.0, 4.0),
    HoldingPeriod.MEDIUM_TERM: (2.0, 4.0),
    HoldingPeriod.LONG_TERM: (2.5, 5.0),
}


def compute_levels(
    entry_price: float,
    atr: float,
    holding_period: HoldingPeriod,
) -> tuple[float, float]:
    """Return (stop_loss, take_profit)."""
    stop_mult, tp_mult = ATR_MULTIPLIERS.get(
        holding_period,
        (ATR_STOP_MULTIPLIER, ATR_TAKE_PROFIT_MULTIPLIER),
    )
    stop_loss = entry_price - stop_mult * atr
    take_profit = entry_price + tp_mult * atr
    return round(stop_loss, 2), round(take_profit, 2)


def risk_reward_ratio(entry: float, stop_loss: float, take_profit: float) -> str:
    """Format as e.g. 1:3."""
    risk = entry - stop_loss
    reward = take_profit - entry
    if risk <= 0:
        return "1:0"
    r = reward / risk
    return f"1:{max(0, int(round(r)))}"


def expected_return_pct(entry: float, take_profit: float) -> float:
    return round((take_profit - entry) / entry * 100, 2)


def position_risk_pct(entry: float, stop_loss: float) -> float:
    return round((entry - stop_loss) / entry * 100, 2)
