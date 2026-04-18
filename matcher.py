import re
from scraper import get_driver_page, find_seller_block


def sku_match(html, sku):
    if not html or not sku:
        return False
    return str(sku).lower() in html.lower()


def seller_match(html, seller):
    if not html or not seller:
        return False
    return str(seller).lower() in html.lower()


# 🔥 REAL FIXED PRICE MATCH
def price_match(url, sheet_price, seller):
    try:
        driver = get_driver_page(url)

        block = find_seller_block(driver, seller)

        if not block:
            driver.quit()
            return False

        text = block.text.lower()

        driver.quit()

        # extract all numbers (prices)
        prices = re.findall(r"\d+(?:\.\d+)?", text)

        if not prices:
            return False

        sheet_price = str(int(float(sheet_price)))

        return sheet_price in prices

    except:
        return False


def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
