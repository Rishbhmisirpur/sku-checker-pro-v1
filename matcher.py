import re


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


# ---------------- SKU MATCH ----------------
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


# ---------------- SELLER MATCH ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = normalize(seller)

    return seller in html


# ---------------- SELLER BLOCK EXTRACTION ----------------
def get_seller_block(html, seller):
    html_low = html.lower()
    seller = normalize(seller)

    if seller not in html_low:
        return ""

    parts = html_low.split(seller)

    # only nearby content (important fix)
    return parts[1][:4000]


# ---------------- PRICE MATCH (STRICT) ----------------
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price or not seller:
            return False

        block = get_seller_block(html, seller)

        if not block:
            return False

        prices = re.findall(r"\d+(?:\.\d+)?", block)

        if not prices:
            return False

        scraped_price = float(prices[0])
        sheet_price = float(sheet_price)

        return scraped_price == sheet_price

    except:
        return False


# ---------------- FINAL CLASSIFICATION ----------------
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
