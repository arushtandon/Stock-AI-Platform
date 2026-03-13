from fastapi import APIRouter, Depends
from api.auth import require_subscription

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/channels")
def list_alert_channels(_=Depends(require_subscription)):
    """Email, push, Telegram, Slack (placeholder)."""
    return {"channels": ["email", "push", "telegram", "slack"]}


@router.post("/subscribe")
def subscribe_alerts(channel: str, _=Depends(require_subscription)):
    """Subscribe to new pick alerts (placeholder)."""
    return {"subscribed": channel}
