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
    try:
        url = str(row["url"]).strip()
        sku = str(row["sku"])
        seller = str(row["seller"])
        target_price = float(re.sub(r'[^0-9.]', '', str(row["price"])))

        html = fetch_content(url)
        if not html: 
            return row.name, "Network Error", False, False, False

        # 1. SKU Check (Using Logic)
        sku_ok = smart_sku_match(html, sku)
        if not sku_ok:
            return row.name, "SKU Wrong", False, False, False

        # 2. Seller Check (Using Logic)
        seller_ok = seller.lower() in html.lower()
        if not seller_ok:
            return row.name, "Wrong Seller", True, False, False

        # 3. Price Check (Logic + AI double check)
        price_ok = price_match_for_seller(html, seller, target_price)
        
        # --- AI INTERVENTION ---
        # Agar logic fail hota hai, toh Gemini AI ek baar check karega
        if not price_ok:
            # AI ko snippet bhej rahe hain verify karne ke liye
            ai_confirmed = ai_deep_verify(html, sku, seller, target_price)
            if ai_confirmed:
                price_ok = True  # AI ne override kar diya agar use price mil gayi
        
        if not price_ok:
            return row.name, "Price Wrong", True, True, False

        return row.name, "Correct", True, True, True

    except Exception as e:
        return row.name, "System Error", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("🔥 START AI ANALYSIS"):
        progress = st.progress(0)
        table_area = st.empty()
        
        done = 0
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(verify_process, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                idx, status, s_ok, sl_ok, p_ok = future.result()
                
                df.loc[idx, "Status"] = status
                df.loc[idx, "sku_match"] = "✅" if s_ok else "❌"
                df.loc[idx, "seller_match"] = "✅" if sl_ok else "❌"
                df.loc[idx, "price_match"] = "✅" if p_ok else "❌"
                
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

        st.download_button("📥 Download Clean CSV", clean_df.to_csv(index=False), "ai_results.csv", "text/csv")
