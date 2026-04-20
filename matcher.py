import re
import google.generativeai as genai

API_KEY = "AIzaSyC47U5A8CEe9UOgtOEytRrpc5SPDgLFbFg" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def normalize(text):
    """Removes special characters for clean matching"""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def smart_seller_match(html_text, seller_name):
    """Matches seller names even with different separators like Walmart_-_Buildcom"""
    norm_html = normalize(html_text)
    norm_seller = normalize(seller_name)
    return norm_seller in norm_html

def smart_sku_match(html, sku):
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
    html = html.lower()
    # Check using multiple variations of seller name
    norm_seller_search = normalize(seller)
    
    # Simple check first
    if norm_seller_search not in normalize(html):
        return False

    # Find prices in the block where seller is mentioned
    # We use a broad search for price nearby
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
        clean_text = re.sub(r'<[^>]+>', ' ', html)[:15000] # Increased context
        prompt = f"""
        Analyze this text strictly:
        Product SKU: {sku}
        Seller Name: {seller}
        Required Price: {price}
        
        Task: Check if {seller} is selling {sku} for {price}.
        Note: Seller names might have symbols like '-' or '_'. 
        Answer ONLY: YES or NO.
        
        Text:
        {clean_text}
        """
        response = model.generate_content(prompt)
        return "YES" in response.text.upper()
    except:
        return False
