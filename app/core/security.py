from fastapi import Header, HTTPException

from app.core.config import get_settings


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()

    if not settings.api_keys:
        return

    valid_keys = {key.strip() for key in settings.api_keys.split(",") if key.strip()}

    if x_api_key is None or x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
