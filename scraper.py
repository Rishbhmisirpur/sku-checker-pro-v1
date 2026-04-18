import requests
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

session = requests.Session()


# ---------------- DRIVER ----------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


# ---------------- SAFE FETCH ----------------
def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            {"User-Agent": "Mozilla/5.0 Chrome/124"},
            {"User-Agent": "Mozilla/5.0 Safari/537.36"}
        ]

        # 🔥 TRY REQUESTS FIRST (FAST)
        for _ in range(2):
            headers = random.choice(headers_list)

            r = session.get(url, headers=headers, timeout=20)

            if r.status_code == 200 and len(r.text) > 1000:
                return r.text

            time.sleep(1)

        # 🔥 FALLBACK: SELENIUM (JS SUPPORT)
        driver = get_driver()
        driver.get(url)

        time.sleep(5)

        html = driver.page_source
        driver.quit()

        return html

    except Exception as e:
        print("Scraper Error:", e)
        return ""


# ---------------- SELLER BLOCK EXTRACTION ----------------
def get_seller_block(html, seller):
    try:
        html_low = html.lower()
        seller = str(seller).lower().replace(".com", "").replace("www", "")

        if seller not in html_low:
            return ""

        parts = html_low.split(seller)

        # nearby content only (important fix)
        return parts[1][:4000]

    except:
        return ""


# ---------------- PRICE EXTRACTOR ----------------
import re

def extract_price_for_seller(html, seller):
    block = get_seller_block(html, seller)

    if not block:
        return None

    prices = re.findall(r"\d+(?:\.\d+)?", block)

    if not prices:
        return None

    return float(prices[0])
