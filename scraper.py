import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def get_driver_page(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(5)  # JS load wait
    return driver


def get_html(url):
    try:
        driver = get_driver_page(url)
        html = driver.page_source
        driver.quit()
        return html
    except:
        return ""


# 🔥 SELLER SPECIFIC BLOCK FINDER (IMPORTANT)
def find_seller_block(driver, seller):
    try:
        seller = seller.lower()

        # find all elements containing seller text
        elements = driver.find_elements("xpath", f"//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{seller}')]")

        if not elements:
            return None

        # take closest parent container (important fix)
        return elements[0].find_element("xpath", "./ancestor::*[3]")

    except:
        return None


# 🔥 PRICE EXTRACTOR INSIDE BLOCK
def extract_price_from_block(block):
    try:
        text = block.text
        return text
    except:
        return ""
