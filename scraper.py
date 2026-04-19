import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

def fetch_content(url):
    # Try Requests (Fast)
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200 and len(r.text) > 1000:
            return r.text
    except:
        pass
    
    # Fallback to Selenium (Deep Scrape)
    driver = None
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        return driver.page_source
    except:
        return ""
    finally:
        if driver: driver.quit()
