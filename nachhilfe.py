import asyncio
from playwright.async_api import async_playwright
import requests
import time
import os

# === KONFIGURATION ===

LOGIN_URL = os.getenv("LOGIN_URL")
ANFRAGEN_URL = os.getenv("ANFRAGEN_URL")

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER")

print(f"Token: >{PUSHOVER_API_TOKEN}<")
print(f"User: >{PUSHOVER_USER_KEY}<")

def sende_push_benachrichtigung(titel, nachricht=""):
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": titel,
        "message": nachricht
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    if response.status_code == 200:
        print("✅ Push gesendet:", nachricht)
    else:
        print("❌ Fehler bei Push:", response.text)


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🌐 Login...")
        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")
        sende_push_benachrichtigung("📍 Aktuelle Seite:", str(page.url))

        try:
            await page.wait_for_selector('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', timeout=5000)
            await page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
            sende_push_benachrichtigung("🍪 Cookie akzeptiert.", "f")
        except:
            sende_push_benachrichtigung("🍪 Kein Cookie-Banner gefunden.", "f")

        await page.wait_for_selector('input[name="loginemail"]', timeout=10000)
        await page.fill('input[name="loginemail"]', EMAIL)
        await page.fill('input[name="loginpassword"]', PASSWORD)

        
        login_xpath = '//*[@id="loginform"]/form/p[3]/input'
        login_button_clicked = False
        for frame in page.frames:
            btn = await frame.query_selector(f'xpath={login_xpath}')
            if btn:
                await btn.click()
                print(f"✅ Login-Button im Frame {frame.url} geklickt.")
                sende_push_benachrichtigung("✅ Login Button gedrückt", f"Frame: {frame.url}")
                login_button_clicked = True
                break
                
        await page.wait_for_timeout(3000)
        await page.goto(ANFRAGEN_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        sende_push_benachrichtigung(await page.url())
        sende_push_benachrichtigung(await page.content())

        try:
            await page.wait_for_selector(
            'xpath=//*[@id="online-anfragen-div"]//p[contains(text(), "Zur Zeit keine Anfragen verfügbar.")]',
            timeout=5000
             )
            sende_push_benachrichtigung("📭 Keine neue Anfrage.")
        except asyncio.TimeoutError:
            print("🎉 Neue Anfrage gefunden!")
            sende_push_benachrichtigung("Neue Anfrage!", "Du hast eine neue Anfrage.")
        
        await browser.close()

async def run_script():
    sende_push_benachrichtigung("Skript gestartet", "Das Playwright-Skript läuft jetzt.")
    while True:
        try:
            await check()
        except Exception as e:
            sende_push_benachrichtigung("Fehler im Skript", str(e))
            print("❌ Fehler:", e)
        await asyncio.sleep(60)
















