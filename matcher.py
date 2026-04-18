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

    html = html.lower()
    seller = str(seller).lower()

    # 🔥 super loose match (fix for real websites)
    return any(word in html for word in seller.split() if len(word) > 3)


# ---------------- PRICE (FINAL FIXED LOGIC) ----------------
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price or not seller:
            return False

        html_low = html.lower()
        seller = normalize(seller)

        # seller must exist somewhere
        if seller.split(".")[0] not in html_low:
            return False

        sheet_price = str(int(float(sheet_price)))

        # 🔥 SIMPLE GLOBAL PRICE CHECK (STABLE)
        prices = re.findall(r"\d+(?:\.\d+)?", html_low)

        return sheet_price in prices

    except:
        return False


# ---------------- FINAL DECISION ----------------
def classify(sku_ok, seller_ok, price_ok):
    return "YES" if (sku_ok and seller_ok and price_ok) else "NO"
