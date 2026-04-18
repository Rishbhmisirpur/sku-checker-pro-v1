from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")

    return webdriver.Chrome(options=options)


def get_html(url):
    try:
        driver = get_driver()
        driver.get(url)

        # 🔥 IMPORTANT WAIT (fix JS sites)
        time.sleep(10)

        html = driver.page_source

        driver.quit()

        if not html or len(html) < 1000:
            return ""

        return html

    except Exception as e:
        print("SCRAPER ERROR:", e)
        return ""
