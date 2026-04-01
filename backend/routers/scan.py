from typing import Any, Dict, List, Optional

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

from core.scanner import FileScanner

router = APIRouter()


class QuickScanRequest(BaseModel):
    include_appdata: bool = True
    paths: Optional[List[str]] = None
    max_files_per_category: int = 100


@router.websocket("/ws/scan")
async def scan_websocket(websocket: WebSocket):
    await websocket.accept()
    config = await websocket.receive_json()
    scanner = FileScanner()
    count = 0
    for file_info in scanner.scan(include_appdata=config.get("include_appdata", True)):
        count += 1
        if count % 10 == 0:
            await websocket.send_json(
                {
                    "type": "progress",
                    "count": count,
                    "total_size": scanner.total_size,
                    "current_file": file_info["path"],
                }
            )
        await websocket.send_json({"type": "file", "data": file_info})

    await websocket.send_json(
        {"type": "complete", "total_files": count, "total_size": scanner.total_size}
    )
    await websocket.close()


@router.post("/quick-scan")
async def quick_scan(body: QuickScanRequest) -> Dict[str, Any]:
    scanner = FileScanner()
    results: Dict[str, Any] = {
        "categories": {},
        "total_files": 0,
        "total_size": 0,
    }
    for file_info in scanner.scan(
        paths=body.paths, include_appdata=body.include_appdata
    ):
        cat = file_info["category"]
        if cat not in results["categories"]:
            results["categories"][cat] = {"count": 0, "size": 0, "files": []}
        bucket = results["categories"][cat]
        bucket["count"] += 1
        bucket["size"] += file_info["size"]
        if len(bucket["files"]) < body.max_files_per_category:
            bucket["files"].append(file_info)
        results["total_files"] += 1
        results["total_size"] += file_info["size"]
    return results
