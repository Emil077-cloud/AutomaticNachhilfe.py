import asyncio
from playwright.async_api import async_playwright
import requests
import os

# === KONFIGURATION ===

LOGIN_URL = os.getenv("LOGIN_URL")
ANFRAGEN_URL = os.getenv("ANFRAGEN_URL")

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER")


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
        print("🚀 Starte Browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="de-DE"
        )
        page = await context.new_page()


        print("🌍 Öffne Login-URL:", LOGIN_URL)
        try:
            await page.goto(LOGIN_URL, timeout=15000)
            await page.wait_for_load_state("networkidle")
            print("✅ Login-Seite geladen.")
        except Exception as e:
            await page.screenshot(path="/tmp/login_error.png")
            raise Exception(f"❌ Fehler beim Laden der Login-Seite: {e}")

        await page.wait_for_timeout(1000)

        # Cookie-Banner wegklicken
        try:
            await page.wait_for_selector('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', timeout=5000)
            await page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            print("🍪 Cookie akzeptiert.")
        except:
            print("🍪 Kein Cookie-Banner gefunden.")

        # Login-Daten einfügen
        await page.wait_for_selector('input[name="loginemail"]', timeout=10000)
        await page.fill('input[name="loginemail"]', EMAIL)
        await page.fill('input[name="loginpassword"]', PASSWORD)

        # Login-Button klicken (erst auf Seite, dann in Frames)
        login_xpath = '//*[@id="loginform"]/form/p[3]/input'
        login_button_clicked = False

        # 1. Direkt auf der Seite
        btn = await page.query_selector(f'xpath={login_xpath}')
        if btn:
            await btn.scroll_into_view_if_needed()
            await btn.wait_for_element_state("visible")
            await btn.wait_for_element_state("enabled")
            await btn.click(force=True)
            login_button_clicked = True
            print("✅ Login-Button direkt auf Seite geklickt.")
        else:
            # 2. In Frames suchen
            for frame in page.frames:
                try:
                    btn = await frame.query_selector(f'xpath={login_xpath}')
                    if btn:
                        await btn.scroll_into_view_if_needed()
                        await btn.wait_for_element_state("visible")
                        await btn.wait_for_element_state("enabled")
                        await btn.click(force=True)
                        login_button_clicked = True
                        print(f"✅ Login-Button im Frame {frame.url} geklickt.")
                        break
                except:
                    continue

        if not login_button_clicked:
            raise Exception("Login-Button konnte nicht gefunden oder geklickt werden.")

        # Zu den Anfragen wechseln
        try:
            await page.goto(ANFRAGEN_URL, timeout=15000)
            await page.wait_for_load_state("networkidle")
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Anfragenseite: {e}")

        # Prüfen ob Anfragen da sind
        try:
            await page.wait_for_selector(
                'xpath=//*[contains(text(), "keine Anfragen verfügbar")]',
                timeout=5000,
                state="visible"
            )
            print("📭 Keine neuen Anfragen.")
        except:
            print("🎉 Neue Anfrage gefunden!")
            sende_push_benachrichtigung("Neue Anfrage!", "Du hast eine neue Anfrage.")

        await browser.close()


async def run_script():
    durchläufe = 0
    sende_push_benachrichtigung("Skript gestartet", "Das Playwright-Skript läuft jetzt.")

    while True:
        try:
            await check()
        except Exception as e:
            sende_push_benachrichtigung("Fehler im Skript", str(e))
            print("❌ Fehler:", e)

        durchläufe += 1
        if durchläufe == 720:
            sende_push_benachrichtigung("Skript läuft noch!", "Das Skript läuft bisher seit 12 Stunden flüssig.")
            durchläufe = 0

        await asyncio.sleep(60)




