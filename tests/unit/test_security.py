import pytest
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.security import verify_api_key


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def test_verify_api_key_allows_when_no_keys_configured(monkeypatch) -> None:
    monkeypatch.setenv("API_KEYS", "")

    await verify_api_key(x_api_key=None)


async def test_verify_api_key_accepts_valid_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEYS", "secret-key")

    await verify_api_key(x_api_key="secret-key")


async def test_verify_api_key_rejects_missing_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEYS", "secret-key")

    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key=None)

    assert exc_info.value.status_code == 401


async def test_verify_api_key_rejects_invalid_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEYS", "secret-key")

    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="wrong-key")

    assert exc_info.value.status_code == 401


async def test_verify_api_key_accepts_one_of_multiple_keys(monkeypatch) -> None:
    monkeypatch.setenv("API_KEYS", "key-one,key-two")

    await verify_api_key(x_api_key="key-two")
