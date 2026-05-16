import re
import google.generativeai as genai

API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()


def normalize_sku(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()


def smart_seller_match(html_text, seller_name):
    norm_html = normalize(html_text)
    norm_seller = normalize(seller_name)
    return norm_seller in norm_html


def smart_sku_match(html, sku):
    html_clean = re.sub(
        r'<script.*?>.*?</script>|<style.*?>.*?</style>',
        '',
        html,
        flags=re.DOTALL | re.IGNORECASE
    )

    text = re.sub(r'<[^>]+>', ' ', html_clean)
    text_lower = text.lower()

    sku_raw = str(sku).strip().lower()
    sku_norm = normalize_sku(sku)

    # Exact same SKU format match
    if re.search(rf'(?<![a-zA-Z0-9]){re.escape(sku_raw)}(?![a-zA-Z0-9])', text_lower):
        return True

    # Same complete SKU with different separator:
    # 7701-BN / 7701 BN / 7701_BN / 7701BN
    text_norm = normalize_sku(text)
    if sku_norm and sku_norm in text_norm:
        return True

    return False


def price_match_for_seller(html, seller, target_price):
    html = html.lower()

    norm_seller_search = normalize(seller)

    # seller must exist
    if norm_seller_search not in normalize(html):
        return False

    # find all numbers possible prices
    found_prices = re.findall(r'\d+\.?\d*', html)

    for p in found_prices:
        try:
            if abs(float(p) - float(target_price)) < 0.01:
                return True
        except:
            continue

    return False


def ai_deep_verify(html, sku, seller, price):
    try:
        clean_text = re.sub(r'<[^>]+>', ' ', html)[:15000]

        prompt = f"""
        Analyze this text strictly:
        Product SKU: {sku}
        Seller Name: {seller}
        Required Price: {price}

        Task: Check if {seller} is selling {sku} for {price}.
        Note: Seller names might have symbols like '-' or '_'.

        IMPORTANT:
        - SKU must be EXACT match.
        - Do not allow wrong extra suffix.

        Answer ONLY: YES or NO.

        Text:
        {clean_text}
        """

        response = model.generate_content(prompt)
        return "YES" in response.text.upper()

    except:
        return False
