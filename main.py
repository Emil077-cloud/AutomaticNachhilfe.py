from fastapi import FastAPI
import asyncio
from nachhilfe import run_script  # ← dein Playwright-Loop

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Nachhilfe-Skript läuft ✅"}

@app.on_event("startup")
async def start_background_task():
    print("🚀 Starte Playwright-Hintergrundskript...")
    asyncio.create_task(run_script())
