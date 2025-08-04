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

        
        for frame in page.frames:
        # Suche nach button[name="annehmen"]
        button = await frame.query_selector('button[name="annehmen"]')
        if button:
            anfrage_button = button
            print(f"Button als <button> im Frame {frame.url} gefunden.")
            break
        # Falls kein <button>, suche nach input[name="annehmen"]
        input_button = await frame.query_selector('input[name="annehmen"]')
        if input_button:
            anfrage_button = input_button
            print(f"Button als <input> im Frame {frame.url} gefunden.")
            break

        if anfrage_button:
            try:
                await anfrage_button.click()
                print("✅ Button wurde geklickt.")
                sende_push_benachrichtigung("✅ Bewerbung erfolgreich", "Button wurde gedrückt.")
            except Exception as e:
                print("❌ Fehler beim Klicken:", e)
                sende_push_benachrichtigung("❌ Klick fehlgeschlagen", str(e))
        else:
            print("📭 Kein Button mit name='annehmen' gefunden.")
            sende_push_benachrichtigung("📭 Keine neue Anfrage (Button nicht gefunden).")

        await page.wait_for_timeout(3000)
        await page.goto(ANFRAGEN_URL)
        await page.wait_for_load_state("networkidle")

        try:
            # XPath überprüfen wie bei Selenium
            kein_anfrage_element = await page.query_selector(
                'xpath=//*[@id="online-anfragen-div"]//p[contains(text(), "Zur Zeit keine Anfragen verfügbar.")]'
            )
            if kein_anfrage_element:
                sende_push_benachrichtigung("📭 Keine neue Anfrage.")
            else:
                raise Exception("Element nicht vorhanden = Anfrage vorhanden")
        except:
            print("🎉 Neue Anfrage gefunden!")
            sende_push_benachrichtigung("Neue Anfrage!", "Du hast eine neue Anfrage.")
            if "Mahte" in await page.content() or "Mahtematik" in await page.content():
                try:
                    await page.click('button[name="annehmen"]')
                    sende_push_benachrichtigung("Beworben", "Erfolgreich auf neue Anfrage beworben.")
                except:
                    sende_push_benachrichtigung("Fehler", "Bewerbungs-Knopf nicht gefunden.")
            else:
                sende_push_benachrichtigung("Fehler", "Falsches Fach.")
        
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












