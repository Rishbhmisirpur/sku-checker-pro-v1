import re


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


# ---------------- SKU ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False

    return str(sku).lower() in html.lower()


# ---------------- SELLER ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    return normalize(seller) in html.lower()


# ---------------- PRICE (STABLE LOGIC FIX) ----------------
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price:
            return False

        html_low = html.lower()
        seller = normalize(seller)

        # 🔥 if seller not present → fail safe
        if seller not in html_low:
            return False

        # 🔥 NO SPLIT DEPENDENCY (IMPORTANT FIX)
        # instead search near seller OR full html fallback

        # take small context window around seller
        index = html_low.find(seller)

        if index == -1:
            return False

        context = html_low[index:index + 8000]

        prices = re.findall(r"\d+(?:\.\d+)?", context)

        if not prices:
            return False

        sheet_price = str(int(float(sheet_price)))

        return sheet_price in prices

    except:
        return False


# ---------------- FINAL DECISION ----------------
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
