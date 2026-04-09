import os
import time
import smtplib
import logging
from playwright.sync_api import sync_playwright

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ALERT_PHONE = os.environ.get("ALERT_PHONE", "")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))

URL = "https://www.mindbodyonline.com/explore/locations/the-social-lift"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

already_alerted = False

def fetch_page_text():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(URL, timeout=30000)
            page.wait_for_timeout(8000)
            text = page.inner_text("body")
            return text
        except Exception as e:
            log.error(f"Error fetching page: {e}")
            return ""
        finally:
            browser.close()

def send_text_alert(message):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            email_message = f"Subject: \n\n{message}"
            smtp.sendmail(GMAIL_ADDRESS, ALERT_PHONE, email_message)
        log.info(f"Alert sent to {ALERT_PHONE}")
    except Exception as e:
        log.error(f"Failed to send alert: {e}")

def check_for_may():
    global already_alerted
    if already_alerted:
        log.info("Already alerted — skipping check.")
        return
    log.info("Checking MindBody schedule...")
    text = fetch_page_text()
    if not text:
        log.warning("Got empty page — will retry next cycle.")
        return
    if "May" in text:
        log.info("May schedule detected!")
        send_text_alert("The Social Lift May schedule is LIVE! Book now: https://www.mindbodyonline.com/explore/locations/the-social-lift")
        already_alerted = True
    else:
        log.info("No May dates found yet. Will check again.")

if __name__ == "__main__":
    log.info("Monitor started. Checking every %d seconds.", CHECK_INTERVAL)
    while True:
        check_for_may()
        time.sleep(CHECK_INTERVAL)
