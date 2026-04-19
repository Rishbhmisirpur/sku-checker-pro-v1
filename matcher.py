import re
import google.generativeai as genai

# ==========================================
# CONFIGURATION - Add your API Key here
# ==========================================
API_KEY = "AIzaSyC47U5A8CEe9UOgtOEytRrpc5SPDgLFbFg" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def normalize(text):
    """Removes special characters for clean matching"""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def smart_sku_match(html, sku):
    """Logic to identify the product SKU"""
    html_clean = re.sub(r'<script.*?>.*?</script>|<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    text_norm = normalize(re.sub(r'<[^>]+>', ' ', html_clean))
    sku_norm = normalize(sku)
    
    if sku_norm in text_norm:
        return True
        
    parts = [normalize(p) for p in re.split(r'[-_\s]+', str(sku)) if len(p) >= 3]
    if not parts: return False
    
    match_count = sum(1 for p in parts if p in text_norm)
    return (match_count / len(parts)) >= 0.7

def price_match_for_seller(html, seller, target_price):
    """Logic to find price near the seller name"""
    html, seller = html.lower(), seller.lower()
    if seller not in html:
        return False

    seller_indexes = [m.start() for m in re.finditer(re.escape(seller), html)]
    for idx in seller_indexes:
        # Scan 1600 characters around the seller
        block = html[max(0, idx - 600) : idx + 1000]
        found_prices = re.findall(r'\d+\.?\d*', block)
        for p in found_prices:
            try:
                if abs(float(p) - float(target_price)) < 0.01:
                    return True
            except:
                continue
    return False

def ai_deep_verify(html, sku, seller, price):
    """
    The 'Final Judge' - Gemini AI double-checks 
    when the proximity logic fails.
    """
    try:
        # Clean HTML to save tokens and avoid noise
        clean_text = re.sub(r'<[^>]+>', ' ', html)[:8000] 
        prompt = f"""
        Analyze this text strictly:
        Product SKU: {sku}
        Seller Name: {seller}
        Required Price: {price}
        
        Is the seller '{seller}' selling SKU '{sku}' for exactly {price}? 
        Answer with only one word: YES or NO.
        
        Text Content:
        {clean_text}
        """
        response = model.generate_content(prompt)
        return "YES" in response.text.upper()
    except Exception as e:
        # If AI fails (quota/network), we return False to be safe
        return False
