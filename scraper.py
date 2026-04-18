import requests
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

session = requests.Session()


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0"},
            {"User-Agent": "Chrome/124"},
            {"User-Agent": "Safari/537"}
        ]

        for _ in range(3):
            headers = random.choice(headers_list)
            r = session.get(url, headers=headers, timeout=20)

            if r.status_code == 200 and len(r.text) > 300:
                return r.text

            time.sleep(1)

        driver = get_driver()
        driver.get(url)

        time.sleep(5)

        html = driver.page_source
        driver.quit()

        return html

    except:
        return ""
