from fastapi import APIRouter, Depends
from api.auth import require_subscription

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("")
def get_portfolio(_=Depends(require_subscription)):
    """User's tracked recommendations (placeholder: integrate with user DB)."""
    return {"positions": [], "message": "Track selected recommendations here"}
