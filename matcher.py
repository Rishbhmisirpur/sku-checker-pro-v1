import re
import json


def normalize(text):
    return str(text).lower().replace(".com", "").replace("www", "").strip()


# ---------------- SKU ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False
    return str(sku).lower() in html.lower()


# ---------------- SELLER (LOOSE MATCH - IMPORTANT FIX) ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    html_low = html.lower()
    seller = normalize(seller)

    # 🔥 loose match instead of strict split
    return seller.split(".")[0] in html_low


# ---------------- EXTRACT JSON-LD PRICE ----------------
def extract_jsonld_prices(html):
    try:
        matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)

        prices = []

        for m in matches:
            try:
                data = json.loads(m.strip())

                if isinstance(data, list):
                    data = data[0]

                if isinstance(data, dict):
                    if "offers" in data:
                        offers = data["offers"]

                        if isinstance(offers, dict) and "price" in offers:
                            prices.append(str(offers["price"]))

                        if isinstance(offers, list):
                            for o in offers:
                                if "price" in o:
                                    prices.append(str(o["price"]))

            except:
                continue

        return prices

    except:
        return []


# ---------------- PRICE MATCH (FINAL STABLE LOGIC) ----------------
def price_match(html, sheet_price, seller):
    try:
        if not html or not sheet_price:
            return False

        sheet_price = str(int(float(sheet_price)))

        # 🔥 STEP 1: JSON-LD FIRST (MOST ACCURATE)
        json_prices = extract_jsonld_prices(html)

        if sheet_price in json_prices:
            return True

        # 🔥 STEP 2: fallback HTML scan
        html_prices = re.findall(r"\d+(?:\.\d+)?", html)

        return sheet_price in html_prices

    except:
        return False


# ---------------- FINAL ----------------
def classify(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "YES"
    return "NO"
