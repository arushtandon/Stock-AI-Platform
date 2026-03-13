"""
OAuth and subscription-based access.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
) -> Optional[dict]:
    """Return user if authenticated, else None (for public endpoints)."""
    if api_key:
        # Validate API key (e.g. from DB); placeholder accepts any for dev
        return {"sub": "api_user", "subscription": "premium"}
    if token:
        # Validate JWT; placeholder
        return {"sub": "user", "subscription": "premium"}
    return None


async def require_subscription(
    user: Optional[dict] = Depends(get_current_user_optional),
) -> dict:
    """Require authenticated user with active subscription."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    if user.get("subscription") not in ("premium", "trial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required",
        )
    return user
