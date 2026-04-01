from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from browsers.detector import BrowserDetector

router = APIRouter()
_detector = BrowserDetector()


class BrowserExportRequest(BaseModel):
    browser_id: str
    profile: str
    dest_path: str
    options: Dict[str, bool] = {}


@router.get("/detect")
async def detect_browsers():
    return {"browsers": _detector.detect_installed()}


@router.post("/export")
async def export_browser(req: BrowserExportRequest) -> Dict[str, Any]:
    return _detector.export_profile(
        req.browser_id, req.profile, req.dest_path, req.options
    )
