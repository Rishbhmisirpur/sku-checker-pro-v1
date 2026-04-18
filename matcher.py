import re


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


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
    seller = normalize(seller)

    return seller in html


# 🔥 extract ONLY seller-specific block
def extract_seller_block(html, seller):
    html = html.lower()
    seller = normalize(seller)

    if seller in html:
        parts = html.split(seller)
        if len(parts) > 1:
            return parts[1]  # after seller section

    return ""


# 🔥 STRICT PRICE MATCH (ONLY INSIDE SELLER BLOCK)
def price_match(html, price, seller):
    try:
        if not html or not price or not seller:
            return False

        block = extract_seller_block(html, seller)

        if not block:
            return False

        price = str(int(float(price)))

        # ONLY check inside seller block
        return price in block

    except:
        return False


# 🔥 FINAL DECISION ENGINE
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
