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
time = 0

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

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        try:
            await page.wait_for_selector('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', timeout=5000)
            await page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
            print("🍪 Cookie akzeptiert.")
        except:
            print("🍪 Kein Cookie-Banner gefunden.")

        await page.wait_for_selector('input[name="loginemail"]', timeout=10000)
        await page.fill('input[name="loginemail"]', EMAIL)
        await page.fill('input[name="loginpassword"]', PASSWORD)

        
        login_xpath = '//*[@id="loginform"]/form/p[3]/input'
        login_button_clicked = False
        for frame in page.frames:
            btn = await frame.query_selector(f'xpath={login_xpath}')
            if btn:
                await btn.scroll_into_view_if_needed()
                await btn.wait_for_element_state("visible")
                await btn.wait_for_element_state("enabled")
                await btn.click(force=True)
                print(f"✅ Login-Button im Frame {frame.url} geklickt.")
                login_button_clicked = True
                break
                
        await page.goto(ANFRAGEN_URL)
        await page.wait_for_load_state("networkidle")

        try:
            await page.wait_for_selector(
            'xpath=//*[@id="online-anfragen-div"]//p[contains(text(), "Zur Zeit keine Anfragen verfügbar.")]',
            timeout=5000,
            state="visible"  # Das ist default, kann aber explizit angegeben werden
        )
            print("Keine Anfrage gefunden.")
        except Exception as e:
            print("🎉 Neue Anfrage gefunden!")
            sende_push_benachrichtigung("Neue Anfrage!", "Du hast eine neue Anfrage.")
        await browser.close()

async def run_script():
    sende_push_benachrichtigung("Skript gestartet", "Das Playwright-Skript läuft jetzt.")
    print("Skript gestartet.")
    while True:
        try:
            await check()
        except Exception as e:
            sende_push_benachrichtigung("Fehler im Skript", str(e))
            print("❌ Fehler:", e)
        time += 1
        if time == 720:
            sende_push_benachrichtigung("Skript läuft noch!", "Das Skript läuft bisher seit 12 Stunden flüssig.")
            time = 0
        await asyncio.sleep(60)



























