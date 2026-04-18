import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def fetch_requests(url):
    try:
        r = session.get(url, timeout=8)
        if r.status_code == 200:
            return r.text.lower()
    except:
        return ""
    return ""

def fetch_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        time.sleep(5)

        html = driver.page_source.lower()
        driver.quit()

        return html
    except:
        return ""

def get_html(url):
    html = fetch_requests(url)
    if not html:
        html = fetch_selenium(url)
    return html
