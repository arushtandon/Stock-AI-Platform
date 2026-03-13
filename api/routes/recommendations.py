from fastapi import APIRouter, Query, Depends
from datetime import datetime
from api.auth import get_current_user_optional
from database.repository import get_latest_recommendations
from config import TOP_N_RECOMMENDATIONS

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list)
def list_recs(
    since: datetime | None = Query(None),
    limit: int = Query(TOP_N_RECOMMENDATIONS, ge=1, le=100),
    _=Depends(get_current_user_optional),
):
    return get_latest_recommendations(since=since, limit=limit)
