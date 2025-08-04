from fastapi import FastAPI
import asyncio
from nachhilfe import run_script

app = FastAPI()

@app.get("/")
async def root():
    # Führt dein Skript im Hintergrund aus
    asyncio.create_task(run_script())
    return {"status": "Script started"}
