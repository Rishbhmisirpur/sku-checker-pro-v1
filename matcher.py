import os
import re
from openai import OpenAI

# ---------------- SAFE OPENAI CLIENT ----------------
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


# ---------------- CLEAN ----------------
def clean_text(text):
    if not text:
        return ""
    return str(text).lower().strip()


# ---------------- SMART SKU MATCH (RULE BASED) ----------------
def smart_sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = clean_text(sku)

    # exact match
    if sku in html:
        return True

    # numeric match (important for SKUs like H1036701S-AGB)
    sku_nums = re.findall(r"\d+", sku)
    html_nums = re.findall(r"\d+", html)

    if sku_nums and html_nums:
        if sku_nums[0] in html_nums:
            return True

    # partial token match
    sku_tokens = set(sku.split())
    html_tokens = set(re.findall(r"[a-z0-9]+", html))

    if len(sku_tokens & html_tokens) >= 1:
        return True

    return False


# ---------------- SMART SELLER MATCH ----------------
def smart_seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = clean_text(seller).replace(".com", "").replace("www", "")

    # direct match
    if seller in html:
        return True

    # token match
    seller_tokens = set(seller.split())
    html_tokens = set(re.findall(r"[a-z0-9]+", html))

    if len(seller_tokens & html_tokens) >= 1:
        return True

    return False


# ---------------- CLEAN PRICE ----------------
def clean_price(price):
    try:
        return float(re.sub(r"[^0-9.]", "", str(price)))
    except:
        return 0


# ---------------- PRICE MATCH (STRICT NUMERIC) ----------------
def price_match_for_seller(html, seller, price):
    try:
        if not html or not price:
            return False

        price = float(price)
        html_prices = re.findall(r"\d+\.?\d*", html)
        html_prices = [float(p) for p in html_prices if p.replace(".", "").isdigit()]

        for p in html_prices:
            if abs(p - price) <= (price * 0.05):  # 5% tolerance
                return True

        return False

    except:
        return False


# ---------------- AI SKU MATCH (OPTIONAL) ----------------
def ai_sku_match(html, sku):
    try:
        if not html or not sku:
            return False

        # fallback if no API key
        if client is None:
            return smart_sku_match(html, sku)

        prompt = f"""
Check if this SKU exists in the content.

SKU: {sku}

CONTENT:
{html[:1500]}

Answer ONLY YES or NO.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        ans = response.choices[0].message.content.lower()
        return "yes" in ans

    except:
        return smart_sku_match(html, sku)
