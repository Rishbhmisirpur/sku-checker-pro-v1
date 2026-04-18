# matcher.py
import re


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
    seller = str(seller).lower().replace(".com", "")

    return seller in html


# ---------------- PRICE MATCH ----------------
def price_match(html, price):
    try:
        if not html or not price:
            return False

        return str(int(float(price))) in html

    except:
        return False


# ---------------- CLASSIFY ----------------
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "MATCH"
    elif sku_ok:
        return "PARTIAL"
    else:
        return "NO MATCH"
