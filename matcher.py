import re


# ---------------- SKU MATCH ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = str(sku).lower().strip()

    if sku in html:
        return True

    sku_nums = re.findall(r"\d+", sku)
    html_nums = re.findall(r"\d+", html)

    if sku_nums and html_nums:
        return sku_nums[0] in html_nums

    return False


# ---------------- SELLER MATCH (IMPROVED) ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()

    seller = str(seller).lower().replace(".com", "").replace("www", "").strip()

    # strong partial match
    seller_tokens = seller.split()
    return any(token in html for token in seller_tokens)


# ---------------- PRICE MATCH ----------------
def price_match(html, price):
    try:
        if not html or not price:
            return False

        price = str(int(float(price)))
        return price in html

    except:
        return False


# ---------------- FINAL LOGIC (IMPORTANT FIX) ----------------
def classify(sku_ok, seller_ok, price_ok):
    # ✔ MAIN RULE
    if sku_ok and seller_ok:
        return "YES"
    return "NO"
