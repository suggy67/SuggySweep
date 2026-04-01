from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import ai, apps, backup, browsers, drives, programs, scan, system

app = FastAPI(title="Suggy Sweep Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(drives.router, prefix="/api/drives", tags=["drives"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(backup.router, prefix="/api/backup", tags=["backup"])
app.include_router(browsers.router, prefix="/api/browsers", tags=["browsers"])
app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
app.include_router(programs.router, prefix="/api/programs", tags=["programs"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
