from fastapi import APIRouter, Query, Depends
from api.auth import require_subscription

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("")
def get_performance(
    days: int = Query(30, ge=1, le=365),
    _=Depends(require_subscription),
):
    """Historical performance: win rate, avg return, equity curve (placeholder)."""
    return {
        "win_rate": 0.0,
        "average_return_pct": 0.0,
        "max_drawdown_pct": 0.0,
        "equity_curve": [],
        "monthly_returns": [],
    }
