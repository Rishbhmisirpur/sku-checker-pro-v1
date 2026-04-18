import re
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None


def clean(t):
    return str(t).lower().strip() if t else ""


def sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = clean(sku)

    if sku in html:
        return True

    nums = re.findall(r"\d+", sku)
    html_nums = re.findall(r"\d+", html)

    if nums and html_nums and nums[0] in html_nums:
        return True

    return False


def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = clean(seller).replace(".com", "")

    return seller in html


def price_match(html, price):
    try:
        price = float(str(price).replace(",", ""))
        return str(int(price)) in html
    except:
        return False


def ai_sku_match(html, sku):
    try:
        if not client:
            return sku_match(html, sku)

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"SKU {sku} exists? YES or NO\n{html[:1200]}"}]
        )

        return "yes" in res.choices[0].message.content.lower()

    except:
        return sku_match(html, sku)


def classify(sku, seller, price):
    if sku and seller and price:
        return "PERFECT"
    elif sku and seller:
        return "PARTIAL"
    elif sku:
        return "SKU ONLY"
    return "NO MATCH"
