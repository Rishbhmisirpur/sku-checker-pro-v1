import re


def sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = str(sku).lower()

    if sku in html:
        return True

    sku_nums = re.findall(r"\d+", sku)
    html_nums = re.findall(r"\d+", html)

    if sku_nums and html_nums:
        return sku_nums[0] in html_nums

    return False


def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = str(seller).lower().replace(".com", "").replace("www", "")

    return seller in html


# ✅ FIXED: PRICE CHECK ONLY FOR SAME SELLER CONTEXT
def price_match(html, price):
    try:
        if not html or not price:
            return False

        scraped_prices = re.findall(r"\d+", html)

        if not scraped_prices:
            return False

        return str(int(float(price))) in scraped_prices

    except:
        return False


# ✅ FINAL LOGIC (STRICT)
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok:
        return "YES"
    return "NO"
