import re
import google.generativeai as genai

# Configure Gemini (Replace 'AIzaSyC47U5A8CEe9UOgtOEytRrpc5SPDgLFbFg' with your actual key)
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def smart_sku_match(html, sku):
    html_clean = re.sub(r'<script.*?>.*?</script>|<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    text_norm = normalize(re.sub(r'<[^>]+>', ' ', html_clean))
    sku_norm = normalize(sku)
    if sku_norm in text_norm: return True
    parts = [normalize(p) for p in re.split(r'[-_\s]+', str(sku)) if len(p) >= 3]
    if not parts: return False
    match_count = sum(1 for p in parts if p in text_norm)
    return (match_count / len(parts)) >= 0.7

def price_match_for_seller(html, seller, target_price):
    html, seller = html.lower(), seller.lower()
    if seller not in html: return False
    seller_indexes = [m.start() for m in re.finditer(re.escape(seller), html)]
    for idx in seller_indexes:
        block = html[max(0, idx - 600) : idx + 1200] # Slightly larger block for safety
        found_prices = re.findall(r'\d+\.?\d*', block)
        for p in found_prices:
            try:
                if abs(float(p) - float(target_price)) < 0.01:
                    return True
            except: continue
    return False

def ai_verify(html_snippet, sku, seller, price):
    """Real AI logic to confirm the findings"""
    prompt = f"""
    Analyze this web content snippet.
    Product SKU: {sku}
    Target Seller: {seller}
    Expected Price: {price}
    
    Tasks:
    1. Is the SKU mentioned?
    2. Is the Seller mentioned?
    3. Is the price {price} linked directly to {seller}?
    
    Return ONLY JSON: {{"sku_found": bool, "seller_found": bool, "price_matched": bool}}
    """
    try:
        response = model.generate_content(prompt + "\nContent: " + html_snippet[:5000])
        return response.text
    except:
        return None
