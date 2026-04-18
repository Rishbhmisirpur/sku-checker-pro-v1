import re
from scraper import fetch_html
from utils import normalize, clean_price

# SKU MATCH
def smart_sku_match(html, sku):
    html = normalize(html)
    sku = normalize(sku)

    if sku in html:
        return True

    parts = [normalize(p) for p in re.split(r'[-_\s]+', sku) if len(p) >= 3]

    match = sum(1 for p in parts if p in html)

    return len(parts) > 0 and (match / len(parts)) >= 0.7


# SELLER MATCH
def smart_seller_match(html, seller):
    html = html.lower()
    parts = re.split(r'[\W_]+', seller.lower())

    match = sum(1 for p in parts if len(p) >= 3 and p in html)

    return match >= max(1, len(parts)//2)


# PRICE MATCH
def price_match(html, seller, target_price):
    html = html.lower()
    target_price = round(float(target_price), 2)
    seller = seller.lower()

    prices = [round(float(p), 2) for p in re.findall(r'\d+\.?\d*', html)]

    if seller not in html:
        return target_price in prices

    for m in re.finditer(re.escape(seller), html):
        block = html[max(0, m.start()-3000): m.start()+3000]
        block_prices = [round(float(p), 2) for p in re.findall(r'\d+\.?\d*', block)]

        if target_price in block_prices:
            return True

    return target_price in prices


# FINAL VERIFY
def verify_row(row):
    url = row["url"]

    html = fetch_html(url)
    if not html:
        return {
            "index": row.name,
            "result": "Error",
            "sku": False,
            "seller": False,
            "price": False,
            "sku_val": row["sku"],
            "seller_val": row["seller"],
            "price_val": row["price"]
        }

    sku_ok = smart_sku_match(html, row["sku"])
    seller_ok = smart_seller_match(html, row["seller"])
    price_ok = price_match(html, row["seller"], clean_price(row["price"]))

    if not sku_ok:
        result = "SKU Wrong"
    elif not seller_ok:
        result = "Seller Wrong"
    elif not price_ok:
        result = "Price Wrong"
    else:
        result = "Correct"

    return {
        "index": row.name,
        "result": result,
        "sku": sku_ok,
        "seller": seller_ok,
        "price": price_ok,
        "sku_val": row["sku"],
        "seller_val": row["seller"],
        "price_val": row["price"]
    }
