import secrets

from fastapi import Header, HTTPException

from app.config import INTERNAL_API_KEY, logger


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-Api-Key")
):
    print(f"Received API key: {x_internal_api_key}")
    if not INTERNAL_API_KEY:
        logger.error("INTERNAL_API_KEY is not configured")
        raise HTTPException(status_code=500, detail="Server authentication is not configured")

    if not x_internal_api_key or not secrets.compare_digest(x_internal_api_key, INTERNAL_API_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")
