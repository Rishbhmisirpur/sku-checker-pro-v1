def smart_sku_match(html, sku):
    return str(sku).lower() in html.lower()

def smart_seller_match(html, seller):
    return str(seller).lower() in html.lower()

def clean_price(price):
    try:
        return float(str(price).replace(",", "").strip())
    except:
        return 0

def price_match_for_seller(html, seller, price):
    return str(price) in html

# 🔥 AI MATCH (simple safe version)
def ai_sku_match(html, sku):
    try:
        # simple smart check (AI jaisa behavior without API)
        return str(sku).lower() in html.lower()
    except:
        return False
