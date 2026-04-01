from fastapi import APIRouter

from core.system_detector import SystemDetector

router = APIRouter()


@router.get("/info")
async def system_info():
    return SystemDetector.detect()
