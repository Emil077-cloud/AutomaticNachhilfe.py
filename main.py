from fastapi import FastAPI
from fastapi.responses import FileResponse
import asyncio
import os
from nachhilfe import run_script  # ← dein Playwright-Loop

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Nachhilfe-Skript läuft ✅"}

@app.get("/screenshot")
async def screenshot():
    pfad = "/tmp/login_error.png"
    if os.path.exists(pfad):
        return FileResponse(pfad, media_type="image/png", filename="login_error.png")
    return {"error": "Noch kein Screenshot vorhanden."}

@app.on_event("startup")
async def start_background_task():
    print("🚀 Starte Playwright-Hintergrundskript...")
    asyncio.create_task(run_script())
