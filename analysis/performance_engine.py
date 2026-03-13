"""
Performance engine for recommendations.

Assumptions:
- Capital per position: fixed USD 100,000
- Quantity = capital / entry_price (no leverage)
- Unrealized PnL = (current_price - entry_price) * quantity
- Return % = (current_price - entry_price) / entry_price * 100
- Hit status:
  - "TP" if current_price >= take_profit
  - "SL" if current_price <= stop_loss
  - "OPEN" otherwise
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from config import TOP_N_RECOMMENDATIONS
from database.models import RecommendationModel

CAPITAL_PER_POSITION = 100_000.0

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - yfinance is in requirements for production
    yf = None


@dataclass
class PositionPerf:
    symbol: str
    entry_price: float
    current_price: float
    pnl_usd: float
    return_pct: float
    margin_used: float
    status: str  # TP / SL / OPEN


def _get_current_price(symbol: str) -> float | None:
    if yf is None:
        return None
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        price = info.get("regularMarketPrice")
        if price is not None:
            return float(price)
        hist = t.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        return None
    return None


def compute_portfolio_performance(session: Session) -> Dict[str, Any]:
    """Compute combined and per-position performance from latest recommendations."""
    # latest TOP_N_RECOMMENDATIONS per published_at
    recs: List[RecommendationModel] = (
        session.query(RecommendationModel)
        .order_by(RecommendationModel.published_at.desc())
        .limit(TOP_N_RECOMMENDATIONS)
        .all()
    )

    positions: List[PositionPerf] = []
    for r in recs:
        if not r.entry_price:
            continue
        current = _get_current_price(r.symbol)
        if current is None:
            continue
        qty = CAPITAL_PER_POSITION / float(r.entry_price)
        pnl_usd = (current - float(r.entry_price)) * qty
        return_pct = (current - float(r.entry_price)) / float(r.entry_price) * 100.0
        status = "OPEN"
        if r.take_profit and current >= float(r.take_profit):
            status = "TP"
        elif r.stop_loss and current <= float(r.stop_loss):
            status = "SL"
        positions.append(
            PositionPerf(
                symbol=r.symbol,
                entry_price=float(r.entry_price),
                current_price=float(current),
                pnl_usd=float(pnl_usd),
                return_pct=float(return_pct),
                margin_used=CAPITAL_PER_POSITION,
                status=status,
            )
        )

    total_notional = CAPITAL_PER_POSITION * len(positions)
    total_pnl = sum(p.pnl_usd for p in positions)
    avg_return = (sum(p.return_pct for p in positions) / len(positions)) if positions else 0.0
    wins = sum(1 for p in positions if p.return_pct > 0)
    win_rate = (wins / len(positions) * 100.0) if positions else 0.0

    # simple max drawdown on equity curve (cumulative pnl)
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for p in positions:
        equity += p.pnl_usd
        if equity > peak:
            peak = equity
        dd = (equity - peak) / CAPITAL_PER_POSITION if CAPITAL_PER_POSITION else 0.0
        if dd < max_dd:
            max_dd = dd

    return {
        "capital_per_position": CAPITAL_PER_POSITION,
        "total_positions": len(positions),
        "total_notional": total_notional,
        "unrealized_pnl_usd": total_pnl,
        "unrealized_pnl_pct": (total_pnl / total_notional * 100.0) if total_notional else 0.0,
        "average_return_pct": avg_return,
        "win_rate_pct": win_rate,
        "max_drawdown_pct": max_dd * 100.0,
        "positions": [
            {
                "symbol": p.symbol,
                "entry_price": p.entry_price,
                "current_price": p.current_price,
                "pnl_usd": p.pnl_usd,
                "return_pct": p.return_pct,
                "margin_used": p.margin_used,
                "status": p.status,
            }
            for p in positions
        ],
    }

