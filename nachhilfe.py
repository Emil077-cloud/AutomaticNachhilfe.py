import asyncio
from playwright.async_api import async_playwright
import requests
import time

# === KONFIGURATION ===

LOGIN_URL = "LOGIN_URL"
ANFRAGEN_URL = "ANFRAGEN_URL"

EMAIL = "LOGIN_EMAIL"
PASSWORD = "LOGIN_PASSWORD"

PUSHOVER_USER_KEY = "PUSHOVER_USER"
PUSHOVER_API_TOKEN = "PUSHOVER_API"

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

        try:
            await page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
            print("🍪 Cookie akzeptiert.")
        except:
            print("🍪 Kein Cookie-Banner gefunden.")

        await page.fill('input[name="loginemail"]', EMAIL)
        await page.fill('input[name="loginpassword"]', PASSWORD)
        await page.click('button[name="login"]')

        await page.wait_for_timeout(3000)
        await page.goto(ANFRAGEN_URL)

        try:
            # XPath überprüfen wie bei Selenium
            kein_anfrage_element = await page.query_selector(
                'xpath=//*[@id="online-anfragen-div"]//p[contains(text(), "Zur Zeit keine Anfragen verfügbar.")]'
            )
            if kein_anfrage_element:
                print("📭 Keine neue Anfrage.")
            else:
                raise Exception("Element nicht vorhanden = Anfrage vorhanden")
        except:
            print("🎉 Neue Anfrage gefunden!")
            if "Mahte" in await page.content() or "Mahtematik" in await page.content():
                try:
                    await page.click('button[name="bewerben"]')
                    sende_push_benachrichtigung("Beworben", "Erfolgreich auf neue Anfrage beworben.")
                except:
                    sende_push_benachrichtigung("Fehler", "Bewerbungs-Knopf nicht gefunden.")
        
        await browser.close()

async def loop():
    sende_push_benachrichtigung("Skript gestartet", "Das Playwright-Skript läuft jetzt.")
    while True:
        try:
            await check()
        except Exception as e:
            sende_push_benachrichtigung("Fehler im Skript", str(e))
            print("❌ Fehler:", e)
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(loop())
