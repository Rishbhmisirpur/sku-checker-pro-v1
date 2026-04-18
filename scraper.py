import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def fetch_html(url):

    # requests first
    for _ in range(2):
        try:
            r = session.get(url, timeout=8)
            if r.status_code == 200:
                return r.text.lower()
        except:
            pass
        time.sleep(1)

    # selenium fallback
    try:
        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(url)
        time.sleep(5)

        html = driver.page_source.lower()
        driver.quit()

        return html

    except:
        return ""
