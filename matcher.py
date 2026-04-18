import re


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


def sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = str(sku).lower()

    return sku in html


def seller_match(html, seller):
    if not html or not seller:
        return False

    return normalize(seller) in html.lower()


# 🔥 STEP 1: GET SELLER SECTION PROPERLY
def get_seller_section(html, seller):
    html_low = html.lower()
    seller = normalize(seller)

    if seller not in html_low:
        return ""

    # split around seller
    parts = html_low.split(seller)

    # take only nearby content (next 2000 chars approx)
    return parts[1][:2000]


# 🔥 STEP 2: STRICT PRICE MATCH INSIDE SELLER BLOCK
def price_match(html, price, seller):
    try:
        if not html or not price or not seller:
            return False

        section = get_seller_section(html, seller)

        if not section:
            return False

        price = str(int(float(price)))

        # ONLY within seller section
        prices_found = re.findall(r"\d+", section)

        return price in prices_found

    except:
        return False


def classify(sku_ok, seller_ok, price_ok):
    # 🔥 STRICT RULE
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
