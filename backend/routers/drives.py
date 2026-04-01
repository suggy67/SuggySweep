from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backup.drive_manager import DriveManager

router = APIRouter()
_manager = DriveManager()


class CheckSpaceRequest(BaseModel):
    drive: str = Field(..., description="Буква диска, например D")
    required_bytes: int = 0


@router.get("/list")
async def list_drives() -> List[Dict[str, Any]]:
    return _manager.get_available_drives()


@router.post("/check-space")
async def check_space(req: CheckSpaceRequest) -> Dict[str, Any]:
    letter = req.drive.rstrip(":").upper()[:1]
    return _manager.check_space(letter, req.required_bytes)
