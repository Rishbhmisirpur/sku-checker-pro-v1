import re


def normalize(t):
    return str(t).lower()


# ---------------- SKU ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False
    return sku.lower() in html.lower()


# ---------------- SELLER ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    return seller.lower().split(".")[0] in html.lower()


# ---------------- PRICE ----------------
def price_match(html, price, seller):
    try:
        if not html or not price:
            return False

        # seller must exist
        if seller.lower().split(".")[0] not in html.lower():
            return False

        price = str(int(float(price)))

        # simple global scan (stable)
        all_prices = re.findall(r"\d+", html)

        return price in all_prices

    except:
        return False


# ---------------- FINAL ----------------
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
