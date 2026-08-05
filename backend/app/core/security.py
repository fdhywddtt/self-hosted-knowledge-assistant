from fastapi import Header, HTTPException

from app.core.config import get_settings


def _resolve_role(x_api_key: str | None) -> str | None:
    settings = get_settings()
    if not settings.enable_auth:
        return "admin"
    if x_api_key in settings.admin_api_keys:
        return "admin"
    if x_api_key in settings.api_keys:
        return "user"
    return None


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if _resolve_role(x_api_key) is None:
        raise HTTPException(status_code=401, detail="无效或缺失 API Key")


async def verify_admin_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if get_settings().enable_auth and _resolve_role(x_api_key) != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")


async def get_current_role(x_api_key: str | None = Header(default=None)) -> str:
    role = _resolve_role(x_api_key)
    if role is None:
        raise HTTPException(status_code=401, detail="无效或缺失 API Key")
    return role
