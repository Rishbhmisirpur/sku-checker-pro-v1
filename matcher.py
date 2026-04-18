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


# ---------------- SELLER BLOCK EXTRACT ----------------
def get_seller_block(html, seller):
    html_low = html.lower()
    seller = normalize(seller)

    if seller not in html_low:
        return ""

    parts = html_low.split(seller)

    # 🔥 ONLY NEARBY TEXT (important fix)
    return parts[1][:5000]


# ---------------- PRICE MATCH (FINAL LOGIC) ----------------
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price or not seller:
            return False

        block = get_seller_block(html, seller)

        if not block:
            return False

        # extract numbers from ONLY seller block
        prices = re.findall(r"\d+(?:\.\d+)?", block)

        if not prices:
            return False

        sheet_price = str(int(float(sheet_price)))

        # 🔥 ONLY check inside seller block
        return sheet_price in prices

    except:
        return False


# ---------------- FINAL DECISION ----------------
def classify(sku_ok, seller_ok, price_ok):
    return "YES" if (sku_ok and seller_ok and price_ok) else "NO"
