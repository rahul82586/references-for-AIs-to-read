from fastapi import APIRouter, Depends
from api.di_providers import get_create_group_handler
from application.commands.create_group import CreateGroupCommand, CreateGroupHandler

router = APIRouter(prefix="/api/v1/admin/groups", tags=["Admin - Groups"])

@router.post("/create")
async def create_group(
    command: CreateGroupCommand,
    handler: CreateGroupHandler = Depends(get_create_group_handler)
):
    """Create a new trading group."""
    group = await handler.handle(command)
    return {"status": "success", "group_id": group.id, "name": group.name}