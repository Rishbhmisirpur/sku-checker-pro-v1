import re


def normalize(t):
    return str(t).lower().replace(".com", "").replace("www", "").strip()


# ---------------- SKU ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False
    return str(sku).lower() in html.lower()


# ---------------- SELLER ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = normalize(seller)

    return seller.split(".")[0] in html


# ---------------- PRICE ----------------
def price_match(html, price, seller):
    try:
        if not html or not price:
            return False

        html_low = html.lower()
        seller = normalize(seller)

        # seller must exist
        if seller.split(".")[0] not in html_low:
            return False

        # extract all numbers
        prices = re.findall(r"\d+(?:\.\d+)?", html_low)

        sheet_price = str(int(float(price)))

        return sheet_price in prices

    except:
        return False


# ---------------- FINAL ----------------
def classify(sku_ok, seller_ok, price_ok):
    return "YES" if (sku_ok and seller_ok and price_ok) else "NO"
