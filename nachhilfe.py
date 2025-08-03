from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import traceback
import os

# === KONFIGURATION ===

LOGIN_URL = os.environ.get("LOGIN_URL")
ANFRAGEN_URL = os.environ.get("ANFRAGEN_URL")
EMAIL = os.environ.get("LOGIN_EMAIL")
PASSWORD = os.environ.get("LOGIN_PASSWORD")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API")

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

def login(driver):
    driver.get(LOGIN_URL)
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        print("🍪 Cookie-Banner akzeptiert.")
    except:
        print("🍪 Kein Cookie-Banner gefunden oder schon akzeptiert.")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "loginemail")))
    driver.find_element(By.NAME, "loginemail").send_keys(EMAIL)
    driver.find_element(By.NAME, "loginpassword").send_keys(PASSWORD)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "login")))
    login_button.click()

def accept_anfrage(driver):
    if "Mathematik" in driver.page_source or "Mathe" in driver.page_source:
        try:
            button = driver.find_element(By.NAME, "bewerben")
            button.click()
            sende_push_benachrichtigung("Erfolgreich beworben", "Eine Mathe-Anfrage wurde automatisch angenommen.")
        except:
            sende_push_benachrichtigung("Fehler", "Knopf drücken hat nicht funktioniert!")
    else:
        sende_push_benachrichtigung("Andere Anfrage", "Die Anfrage ist nicht für Mathe.")

def check_anfragen(driver):
    driver.get(ANFRAGEN_URL)
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, '//*[@id="online-anfragen-div"]//p[contains(text(), "Zur Zeit keine Anfragen verfügbar.")]')
        print("📭 Keine neue Anfrage gefunden.")
    except:
        print("🎉 Neue Anfrage gefunden!")
        accept_anfrage(driver)
        sende_push_benachrichtigung("Neue Anfrage", "Es gibt eine neue Unterrichtsanfrage!")

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    options.binary_location = "/usr/bin/chromium-browser"  # WICHTIG!

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login(driver)
        while True:
            check_anfragen(driver)
            print("Warte 60 Sekunden bis zum nächsten Check...")
            time.sleep(60)
    except Exception as e:
        print("❌ Fehler:", e)
        print(traceback.format_exc())
        sende_push_benachrichtigung("Fehler im Skript", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    sende_push_benachrichtigung("Skript gestartet", "Das Skript läuft jetzt.")
    main()
