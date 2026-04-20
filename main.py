import streamlit as st
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Modular imports
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller, ai_deep_verify
from ui import apply_custom_css, render_stats
from db import save_to_history

st.set_page_config(page_title="SKU AI ANALYZER PRO", layout="wide")
apply_custom_css()

st.title("🛡️ SKU ULTRA PRO MAX + ARM AI")
st.divider()

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def verify_process(row):
    """
    Processes each row to verify SKU, Seller, and Price.
    Logic is modified to ensure all checks run even if one fails.
    """
    idx = row.name
    status_msg = "Processed"
    sku_ok = False
    seller_ok = False
    price_ok = False

    try:
        url = str(row["url"]).strip()
        sku = str(row["sku"])
        seller = str(row["seller"])
        # Clean price string to float
        price_str = re.sub(r'[^0-9.]', '', str(row["price"]))
        target_price = float(price_str) if price_str else 0.0

        html = fetch_content(url)
        if not html: 
            return idx, "Network Error", False, False, False

        # 1. SKU Check
        sku_ok = smart_sku_match(html, sku)

        # 2. Seller Check (Runs regardless of SKU result)
        seller_ok = seller.lower() in html.lower()

        # 3. Price Check (Logic + AI double check)
        price_logic_ok = price_match_for_seller(html, seller, target_price)
        
        if not price_logic_ok:
            # Trigger Gemini AI if standard logic fails
            price_ok = ai_deep_verify(html, sku, seller, target_price)
        else:
            price_ok = True

        # Determine Final Status Message
        if sku_ok and seller_ok and price_ok:
            status_msg = "Correct"
        else:
            # Concatenate errors for better visibility
            errors = []
            if not sku_ok: errors.append("SKU Wrong")
            if not seller_ok: errors.append("Seller Wrong")
            if not price_ok: errors.append("Price Wrong")
            status_msg = " | ".join(errors)

        return idx, status_msg, sku_ok, seller_ok, price_ok

    except Exception as e:
        return idx, f"System Error: {str(e)}", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("🔥 START AI ANALYSIS"):
        progress = st.progress(0)
        table_area = st.empty()
        
        done = 0
        # Initialize columns
        df["Status"] = "Pending"
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verify_process, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                idx, status, s_ok, sl_ok, p_ok = future.result()
                
                df.at[idx, "Status"] = status
                df.at[idx, "sku_match"] = "✅" if s_ok else "❌"
                df.at[idx, "seller_match"] = "✅" if sl_ok else "❌"
                df.at[idx, "price_match"] = "✅" if p_ok else "❌"
                
                done += 1
                progress.progress(done / len(df))
                table_area.dataframe(df.head(done), use_container_width=True)

        st.success("Analysis Finished with Gemini AI!")
        render_stats(df.rename(columns={"Status": "result"}))

        # --- CLEAN CSV DOWNLOAD ---
        clean_df = df.copy()
        mapping = {"✅": "Yes", "❌": "No"}
        for col in ["sku_match", "seller_match", "price_match"]:
            clean_df[col] = clean_df[col].map(mapping)

        st.download_button(
            label="📥 Download Clean CSV",
            data=clean_df.to_csv(index=False),
            file_name="ai_results.csv",
            mime="text/csv"
        )
