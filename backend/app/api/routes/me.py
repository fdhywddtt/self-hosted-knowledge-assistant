from fastapi import APIRouter, Depends

from app.core.security import get_current_role

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=dict)
async def me(role: str = Depends(get_current_role)) -> dict:
    return {"role": role}
