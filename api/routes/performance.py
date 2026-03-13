from fastapi import APIRouter
from analysis.performance_engine import compute_portfolio_performance
from database.repository import Session

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("")
def get_performance():
    """Combined and per-position performance based on latest recommendations.

    Assumes USD 100,000 capital per recommendation.
    """
    session = Session()
    try:
        return compute_portfolio_performance(session)
    finally:
        session.close()
