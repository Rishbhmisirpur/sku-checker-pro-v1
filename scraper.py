from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0")

    return webdriver.Chrome(options=options)


def get_html(url):
    try:
        driver = get_driver()
        driver.get(url)

        time.sleep(7)

        html = driver.page_source
        driver.quit()

        return html

    except:
        return ""
