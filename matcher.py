import re


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


def sku_match(html, sku):
    if not html or not sku:
        return False

    return str(sku).lower() in html.lower()


def seller_match(html, seller):
    if not html or not seller:
        return False

    return normalize(seller) in html.lower()


# 🔥 SMART PRICE EXTRACT (NO BLOCK DEPENDENCY)
def extract_all_prices(html):
    # captures: 586, 586.00, $586, ₹586
    return re.findall(r"\d+(?:\.\d+)?", html)


# 🔥 SELLER + PRICE SMART CHECK
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price:
            return False

        html_low = html.lower()
        seller = normalize(seller)

        # 🔥 STEP 1: ensure seller exists
        if seller not in html_low:
            return False

        # 🔥 STEP 2: extract all prices near seller
        split = html_low.split(seller)

        if len(split) < 2:
            return False

        near_text = split[1][:5000]  # expanded window

        prices = extract_all_prices(near_text)

        if not prices:
            return False

        sheet_price = str(int(float(sheet_price)))

        return sheet_price in prices

    except:
        return False


def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
