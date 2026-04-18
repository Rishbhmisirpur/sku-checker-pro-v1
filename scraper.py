import requests
import random
import time

# Selenium fallback imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


session = requests.Session()


# ---------------- SELENIUM DRIVER ----------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


# ---------------- MAIN SCRAPER (HYBRID) ----------------
def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0"},
            {"User-Agent": "Chrome/124"},
            {"User-Agent": "Safari/537"}
        ]

        # ---------------- 1. FAST MODE (requests) ----------------
        for _ in range(3):
            headers = random.choice(headers_list)

            r = session.get(url, headers=headers, timeout=20)

            html = r.text or ""

            # valid HTML check
            if r.status_code == 200 and len(html) > 300:
                return html

            time.sleep(1)

        # ---------------- 2. FALLBACK MODE (SELENIUM) ----------------
        driver = None
        try:
            driver = get_driver()
            driver.get(url)

            time.sleep(3)  # JS render wait

            html = driver.page_source

            if html and len(html) > 300:
                return html

            return ""

        except:
            return ""

        finally:
            if driver:
                driver.quit()

    except:
        return ""
