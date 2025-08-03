from fastapi import FastAPI
import asyncio
import nachhilfe  # dein Playwright-Skript (leicht angepasst)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(nachhilfe.loop())  # Starte dein Skript beim Booten

@app.get("/")
async def root():
    return {"status": "Läuft"}
