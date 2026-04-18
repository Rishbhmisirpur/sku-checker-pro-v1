# scraper.py
import requests
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


session = requests.Session()


# ---------------- SELENIUM DRIVER ----------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver


# ---------------- MAIN SCRAPER ----------------
def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0"},
            {"User-Agent": "Chrome/124"},
            {"User-Agent": "Safari/537"}
        ]

        # -------- FAST MODE (requests) --------
        for _ in range(3):
            headers = random.choice(headers_list)
            r = session.get(url, headers=headers, timeout=20)

            if r.status_code == 200 and len(r.text) > 300:
                return r.text

            time.sleep(1)

        # -------- FALLBACK (Selenium) --------
        driver = get_driver()
        driver.get(url)

        time.sleep(5)

        html = driver.page_source
        driver.quit()

        return html

    except Exception as e:
        print("SCRAPER ERROR:", e)
        return ""
