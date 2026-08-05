from fastapi import APIRouter, Depends

from app.agents.registry import registry
from app.api.deps import verify_api_key
from app.schemas.agent import AgentInfo

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentInfo], dependencies=[Depends(verify_api_key)])
async def list_agents():
    return [
        AgentInfo(name=agent.name, description=agent.description)
        for agent in registry.list()
    ]
