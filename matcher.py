import os
from openai import OpenAI

# SAFE CLIENT (no crash if key missing)
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


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


# 🔥 AI MATCH (safe)
def ai_sku_match(html, sku):
    try:
        if client is None:
            return str(sku).lower() in html.lower()

        prompt = f"Check if SKU '{sku}' exists in this content. Answer YES or NO.\n\n{html[:1000]}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        ans = response.choices[0].message.content.strip().lower()
        return "yes" in ans

    except:
        return str(sku).lower() in html.lower()
