from fastapi import APIRouter, Query, Depends
from api.auth import require_subscription
from database.repository import get_latest_recommendations

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/stock/{symbol}")
def get_stock_analysis(symbol: str, _=Depends(require_subscription)):
    """Detailed breakdown for a single stock (from latest recommendations or analyses)."""
    recs = get_latest_recommendations(limit=100)
    for r in recs:
        if r["symbol"] == symbol.upper():
            return r
    return {"symbol": symbol, "detail": "Not in latest recommendations"}
