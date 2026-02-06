"""Minimal Samma Suit demo — mount on FastAPI in ~30 lines."""

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from samma import SammaSuit, SUTRASettings, Permission, require_permission
from samma.exceptions import PermissionDeniedError

app = FastAPI(title="Samma Suit Demo")

# One-call setup
suit = SammaSuit(app)
suit.activate_sutra(settings=SUTRASettings(
    allowed_origins=["https://yourapp.com", "http://localhost:*"],
    rate_limit_per_ip=50,
    rate_limit_window_seconds=60,
))
suit.activate_dharma()

# Unprotected route — anyone can access
@app.get("/public")
async def public():
    return {"message": "Hello, world!"}

# Protected route — only agents with ADMIN_WRITE permission
@app.get("/admin")
async def admin(
    _perm=Depends(require_permission(Permission.ADMIN_WRITE)),
):
    return {"message": "Admin access granted"}

# Status dashboard
@app.get("/samma/status")
async def status():
    return suit.status()

# Handle DHARMA permission denials
@app.exception_handler(PermissionDeniedError)
async def on_denied(request: Request, exc: PermissionDeniedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

# Run: uvicorn examples.fastapi_demo:app --reload
