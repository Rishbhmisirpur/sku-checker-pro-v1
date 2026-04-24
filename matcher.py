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


# 🔥 FIXED: STRICT SKU MATCH (NO PARTIAL MATCH)
def smart_sku_match(html, sku):
    # remove scripts/styles
    html_clean = re.sub(r'<script.*?>.*?</script>|<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    
    # remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_clean)
    
    # split into tokens (keeping hyphen important for SKU)
    tokens = re.split(r'[^a-zA-Z0-9\-]+', text)
    
    # normalize sku (lower only, DON'T remove hyphen)
    sku_clean = str(sku).strip().lower()
    
    # normalize tokens
    tokens = [t.strip().lower() for t in tokens if t.strip()]
    
    # exact match only
    for t in tokens:
        if t == sku_clean:
            return True
    
    return False


def price_match_for_seller(html, seller, target_price):
    html = html.lower()
    
    norm_seller_search = normalize(seller)
    
    # seller must exist
    if norm_seller_search not in normalize(html):
        return False

    # find all numbers (possible prices)
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
        - SKU must be EXACT match (no extra suffix like -162 allowed)
        
        Answer ONLY: YES or NO.
        
        Text:
        {clean_text}
        """

        response = model.generate_content(prompt)
        return "YES" in response.text.upper()

    except:
        return False
