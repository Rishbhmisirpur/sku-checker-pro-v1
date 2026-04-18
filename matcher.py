import re

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def smart_sku_match(html, sku):
    text = re.sub(r'<[^>]+>', ' ', html)
    text = normalize(text)
    sku_clean = normalize(sku)

    if sku_clean in text:
        return True

    parts = re.split(r'[-_\s]+', sku.lower())
    parts = [normalize(p) for p in parts if len(p) >= 3]

    match_count = sum(1 for p in parts if p in text)
    return len(parts) > 0 and (match_count / len(parts)) >= 0.7

def smart_seller_match(html, seller):
    html = html.lower()
    parts = re.split(r'[\W_]+', seller.lower())

    match_count = sum(1 for p in parts if len(p) >= 3 and p in html)
    return match_count >= max(1, len(parts)//2)

def clean_price(text):
    try:
        return round(float(re.sub(r'[^0-9.]', '', str(text))), 2)
    except:
        return 0.0

def price_match_for_seller(html, seller, target_price):
    html = html.lower()
    target_price = round(float(target_price), 2)

    prices = [round(float(p), 2) for p in re.findall(r'\d+\.?\d*', html)]
    return target_price in prices
