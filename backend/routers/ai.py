import json
from typing import Dict, List

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ai.lovable_client import LovableAIClient

router = APIRouter()
client = LovableAIClient()


class FileAnalysisRequest(BaseModel):
    file_info: Dict


class ChatRequest(BaseModel):
    messages: List[Dict]


class DirectoryAnalysisRequest(BaseModel):
    dir_path: str
    files: List[str]


@router.post("/analyze-file")
async def analyze_file(request: FileAnalysisRequest):
    async def generate():
        async for chunk in client.analyze_file(request.file_info):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/analyze-directory")
async def analyze_directory(request: DirectoryAnalysisRequest):
    async def generate():
        async for chunk in client.analyze_directory(request.dir_path, request.files):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in client.chat(request.messages):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/recommendations")
async def recommendations(scan_results: Dict = Body(...)):
    async def generate():
        async for chunk in client.get_backup_recommendations(scan_results):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
